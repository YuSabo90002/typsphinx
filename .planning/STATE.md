---
gsd_state_version: 1.0
milestone: v0.6.4
milestone_name: Read the Docs migration
status: Awaiting next milestone
stopped_at: Milestone v0.6.4 closed (audit passed, archived, published)
last_updated: "2026-07-27T21:51:33.264Z"
last_activity: 2026-07-28
last_activity_desc: Milestone v0.6.4 completed and archived
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 33
  completed_plans: 33
  percent: 100
current_phase: 999.1
current_phase_name: BACKLOG
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-28 after v0.6.4 milestone close)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise. For v0.6.4 the same standard applies to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced.
**Current focus:** Planning next milestone (`/gsd-new-milestone`)

## Current Position

Phase: Milestone v0.6.4 complete (closed 2026-07-28, verified_closeout — audit passed 13/13)
Plan: —
Status: Awaiting next milestone (`/gsd-new-milestone`)
Last activity: 2026-07-28 — v0.6.4 closed: archived, PR #124 merged, tagged, published

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

- Total plans completed (project cumulative): 100 (55 through v0.6.2 + 12 in v0.6.3 + 33 in v0.6.4)
- v0.6.3: 6 phases / 12 plans / 28 tasks, 2026-07-23 → 2026-07-25
- v0.6.4: 6 phases / 33 plans / 79 tasks, 2026-07-25 → 2026-07-28 (shipped)

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

### Pending Todos

Five open in `.planning/todos/pending/`, all acknowledged as deferred at the v0.6.4 close
(recorded in Deferred Items below):

- **add-sphinx-linkcheck-ci-job** (ci, docs) — deferred as Future requirement LNK-01; CI-05's
  repo-wide real-HTTP check covers the real failure class.
- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent.
- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening.
- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — do not "modernize" until it lands.
- **derive-typst-lang-duplicated-warning-block** (template_engine) — review IN-01 (Info), waived.

Resolved and filed at close: **github-io-doc-links-404-missing-en-prefix** (Phase 31) and
**docs-usage-installation-orphan-class** (Phase 30) → `todos/completed/`.

### Blockers/Concerns

**Owner-manual steps owed post-close (from `33-HANDOFF.md`, items 4–5):**

- Flip the parent (English) RTD project's **Default branch** from `gsd/v0.6.4-read-the-docs-migration`
  to `main`; same for the Japanese project.
- `.gitmodules` `branch` → `main` in `typsphinx-doc-translations` (the submodule tracks the milestone
  branch — PD-02 carry-forward).
- After the `v0.6.4` tag's RTD build shows green: flip the English project's **Default Version**
  `latest` → `stable`, then re-confirm the ja project's independent version activation and that
  `/ja/stable/` resolves to the same tag as `/en/stable/`. Do **not** flip early — the root redirect
  follows Default Version even when the target doesn't exist yet.

**Three carried Warnings from 30.1's review (quality, not gaps):** `contributing.rst` Translations
section lacks a toolchain-install step; `docs/source/_typst/custom_template.typ` is an unguarded
FOURTH `@preview` version-lockstep site (the sync test watches 3 surfaces + `examples/`); the live
translations-repo manifests have no structural test coverage in this repository.

UI note (standing): this project's phases are typesetting/config/docs/hosting work, **not** frontend
UI — `ui.plan-gate` false-positives on PDF/HTML/template wording; use `--skip-ui`. Same for
`api-coverage.verify-pre` false-positives on prose describing RTD API reads as evidence (three
recorded overrides in v0.6.4). GATE-01 note: honest-verifier — abstain to `human_needed` rather than
assert a truth without direct evidence.

### Roadmap Evolution

Cleared at v0.6.4 close (the milestone's evolution history is preserved in
`milestones/v0.6.4-ROADMAP.md`). Next entries accrue during the next milestone.

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
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Pending backlog | v0.6.2 close |
| Todo (translator, examples) | citation-node-support-untracked | Pending backlog | v0.6.2 close |
| Todo (builder) | non-str-docname-typeerror-in-typstpdf-finish | Pending backlog | v0.6.2 close |
| Todo (typing) | modernize-typing-imports-drop-up006-up035-ignore | Pending backlog | v0.6.2 close |
| Todo (template_engine) | derive-typst-lang-duplicated-warning-block (review IN-01, Info) | Pending backlog | v0.6.3 close |

## Session Continuity

**Resume file:** None

Last session: 2026-07-28
Stopped at: v0.6.4 milestone closed (audit passed → archived → merged → tagged → published)
Resume: `/gsd-new-milestone` — after performing the owner-manual RTD flips listed under
Blockers/Concerns.

## Operator Next Steps

- **Owner-manual (web UI):** the two RTD Default-branch flips → `main`; `.gitmodules` `branch` →
  `main` in `typsphinx-doc-translations`; after the `v0.6.4` tag builds green on RTD, Default
  Version `latest` → `stable` + the ja `/ja/stable/` re-check (details in Blockers/Concerns).
- Start the next milestone with `/gsd-new-milestone`.
