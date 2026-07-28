---
gsd_state_version: 1.0
milestone: v0.6.5
milestone_name: inline-math separator hotfix
current_phase: 34
current_phase_name: inline-math-after-text-separator-fix
status: executing
stopped_at: Phase 34 planned — RESEARCH.md (root cause measured), PATTERNS.md, VALIDATION.md, 3 plans
last_updated: "2026-07-28T13:36:16.756Z"
last_activity: 2026-07-28
last_activity_desc: Phase 34 execution started
progress:
  total_phases: 2
  completed_phases: 0
  total_plans: 3
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-28 after v0.6.4 milestone close)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise. For v0.6.4 the same standard applies to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced.
**Current focus:** Phase 34 — inline-math-after-text-separator-fix

## Current Position

Phase: 34 (inline-math-after-text-separator-fix) — EXECUTING
Plan: 1 of 3
Status: Executing Phase 34
Last activity: 2026-07-28 — Phase 34 execution started

Progress: [--------------------] 0% (0/2 phases)

## Active Milestone (v0.6.5 — inline-math separator hotfix)

**Goal:** Fix backlog item 999.1 — a paragraph where inline math immediately follows text emits Typst
with no valid separator before the `mi(...)` / `$...$` call, so `typst.compile()` aborts — and release
v0.6.5 promptly. Minimal hotfix scope: nothing else enters this milestone.

**Phases:**

| Phase | Goal | Requirements |
|-------|------|--------------|
| 34. Inline Math After Text — Separator Fix | Prose-then-inline-math paragraphs build to PDF on both the mitex and native math paths, pinned by a real-compile fixture proven red pre-fix | MATH-01 |
| 35. v0.6.5 Release Prep | Version bump + curated CHANGELOG with tail link-block rollover; prep-only (publish at `/gsd-complete-milestone`) | REL-03 |

**Coverage:** 2/2 v1 requirements mapped; no orphans.

**Open question Phase 34 must answer by measurement, not assumption:** the backlog note blamed
"`translator.py` math/Text visit ordering," but `visit_math` (`translator.py:3936`) already calls
`_add_paragraph_separator()` (`:3954`). The real root cause is unmeasured — reproduce first, capture
the emitted `.typ` and the verbatim Typst error, then fix what the measurement shows.

**Milestone invariants (every phase):** zero new runtime dependencies; no `@preview` version bump; the
four bundled package version strings unchanged across all four sync surfaces (`writer.py`,
`template_engine.py`, `templates/base.typ`, `examples/**/*.typ`).

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
- v0.6.5: 2 phases / plans TBD, started 2026-07-28

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

Five open in `.planning/todos/pending/`, all acknowledged as deferred at the v0.6.4 close and
explicitly out of v0.6.5 scope (minimal hotfix):

- **add-sphinx-linkcheck-ci-job** (ci, docs) — deferred as Future requirement LNK-01; CI-05's
  repo-wide real-HTTP check covers the real failure class.

- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent.
- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening.
- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — do not "modernize" until it lands.
- **derive-typst-lang-duplicated-warning-block** (template_engine) — review IN-01 (Info), waived.

Resolved and filed at the v0.6.4 close: **github-io-doc-links-404-missing-en-prefix** (Phase 31) and
**docs-usage-installation-orphan-class** (Phase 30) → `todos/completed/`.

### Blockers/Concerns

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

## Session Continuity

**Resume file:** None

Last session: 2026-07-28
Stopped at: Phase 34 planned — RESEARCH.md (root cause measured), PATTERNS.md, VALIDATION.md, 3 plans
verified by plan-checker (all dimensions pass)
Resume: `/gsd-execute-phase 34`.

## Operator Next Steps

- Execute the fix phase with `/gsd-execute-phase 34` (waves are strictly sequential: fixture+RED →
  fix → regression sweep, because SC#4 requires the RED run recorded before the fix lands).

- Root cause is now **measured** (Phase 34 RESEARCH.md): the backlog's top-level-paragraph shape
  already works; the real defect is `visit_math` (and `visit_math_block`) skipping separator
  participation in list-item and concat contexts. Scope decisions D-01 (fix both) and D-02
  (fixture = list item + concat context, RED recorded) are locked in the plans.
