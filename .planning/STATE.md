---
gsd_state_version: 1.0
milestone: v0.6.4
milestone_name: Read the Docs 移行
status: planning
last_updated: "2026-07-25T11:20:45.734Z"
last_activity: 2026-07-25
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-25 at the v0.6.4 milestone start)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise.
**Current focus:** Milestone v0.6.4 — Read the Docs 移行. Defining requirements.

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-07-25 — Milestone v0.6.4 started

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
Milestone branches deleted; only `main` and `gh-pages` remain.

**Closeout type:** `override_closeout` — all 6 phases were `phase_complete` with
`verification_status: passed` and all 7 requirements checked off, but no `v0.6.3-MILESTONE-AUDIT.md`
was produced (owner accepted at close, 2026-07-25: Phase 28's live re-run of the full-corpus gate,
full pytest suite, and both docs-build tox environments already covers the audit's requirement-coverage
and integration ground) and 9 pending todos were acknowledged as deferred (below).

**Closed at close, not deferred:** the bundled `examples/advanced` sample was unbuildable on two
independent axes — five `typst_elements` keys outside the CONF-04 allowlist, and `custom.typ` three
milestones behind on its `@preview` pins (`unknown variable: kai`). Repaired inline before the tag,
with `test_preview_version_sync.py` extended over `examples/**/*.typ` to close the drift channel.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 67 (55 through v0.6.2 + 12 in v0.6.3)
- v0.6.3: 6 phases / 12 plans / 28 tasks, 2026-07-23 → 2026-07-25

*Updated after each plan completion*

## Accumulated Context

### Decisions

Recent decisions affecting current work (full log in PROJECT.md Key Decisions):

- 2026-07-25 [v0.6.3 close]: `examples/` templates joined the `@preview` version-sync guard. A bundled
  sample drifted three milestones behind unnoticed because the guard only watched the three
  extension-internal surfaces; a stale pin there is not cosmetic (it makes the sample fail to compile).

- 2026-07-25 [Phase 27.1]: explicit `typst_elements` precedence made **structural**, not incidental —
  auto-derived `lang` is pre-merged *under* the user's dict, and auto-derivation is gated to the
  bundled-default-template path so custom-template/`typst_package` users are never handed an
  undeclared kwarg.

- 2026-07-24 [Phase 26]: `typst_elements` uses a curated, hand-maintained allowlist that must mirror
  `base.typ`'s `project()` signature. A `.typ` signature can't be introspected from Python, and an
  undeclared kwarg is a hard Typst fatal — so the allowlist fails loud rather than passing through.

- 2026-07-20: `branching_strategy: milestone` — ship unit is the milestone; the final phase is a
  prep-only Release phase, publish deferred to `/gsd-complete-milestone`. Push `main` to `origin` at
  every milestone close.

- 2026-07-22 [Phase 22.2]: dead-config sweep pattern — a config→output real-compile regression fixture
  (template `tests/test_package_only_config_gate.py`) is the bar, so registration-only asserts can't
  hide a dead feature. CONF-04/CONF-05 were the round-2 instances of the same defect class.

### Pending Todos

Eight open in `.planning/todos/pending/` after the v0.6.3 close, all acknowledged as deferred:

- **move-documentation-hosting-to-read-the-docs** (docs) — RTD migration (~2026-07-30 target); the
  github.io 404 doc-link fix is folded into it.

- **add-sphinx-linkcheck-ci-job** (ci, docs) — automate `sphinx-build -b linkcheck`; own ~1-phase task.
- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent;
  surfaced in Phase 22.2, permanent fix unplanned.

- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening, deferred
  from Phase 22.3 (D-06).

- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — deferred; do not "modernize" typing
  imports until this lands.

- **github-io-doc-links-404-missing-en-prefix** (docs) — folded into the RTD migration (owner decision
  2026-07-23), not interim-fixed.

- **derive-typst-lang-duplicated-warning-block** (template_engine) — Phase 27.1 code review IN-01
  (Info), consciously waived.

- **docs-usage-installation-orphan-class** (docs) — `docs/usage.rst` / `docs/installation.rst` are the
  same unreachable-orphan class Phase 27 deleted `docs/configuration.rst` for.

Closed 2026-07-25: **verify-no-gap-between-pr98-and-phase25** (measured gap-free),
**examples-advanced-non-allowlisted-typst-elements-keys** (repaired at milestone close, see above),
and **close-pr98-after-v063-release** (posted + closed after the publish —
[comment](https://github.com/YuSabo90002/typsphinx/pull/98#issuecomment-5078139533)). The PR#98
close surfaced a process lesson: AlCalzone had asked an unanswered question in the thread
("would you rather like to have issues reported with the details instead?"), so the comment was
rewritten to answer it first (owner decision: **PRs are welcome**) rather than post a thank-you
over an open question. Read the whole thread before commenting on someone else's PR.

### Blockers/Concerns

None open. UI note: this project's phases are Typst PDF typesetting / config / docs work, NOT frontend
UI — the `ui.plan-gate` false-positives on PDF/rendering phases; use `--skip-ui` if it flags them.
GATE-01 note (from v0.6.2, still standing): the honest-verifier rule — abstain to `human_needed`
rather than assert a truth without direct evidence.

**Recurring scoping lesson (v0.6.3, twice):** a docs/config success criterion phrased "anywhere under
X" must be checked by a repo-wide grep at discovery time, not against the files the requirement names.
Phase 27 missed `docs/source/examples/*.rst` that way (closed post-verify), and the `examples/`
directory was missed by *both* Phase 26 (fail-loud interaction) and Phase 27 — surfacing only at the
milestone close as an unbuildable shipped sample.

## Deferred Items

Items acknowledged and carried forward from milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |
| Config | CONF-06: `typst_elements` keys beyond papersize/fontsize/**lang** (needs `base.typ` `project()` params) — `lang` は 2026-07-25 に CONF-07 として切り出し v1 昇格（Phase 27.1）、残りは据え置き | Deferred to future milestone | v0.6.3 scoping |
| Verification | No `v0.6.3-MILESTONE-AUDIT.md` produced (owner accepted; Phase 28's live gate re-run stood in) | Accepted at close | v0.6.3 close |
| Todo (docs) | move-documentation-hosting-to-read-the-docs (+ github.io 404 links folded in) | Pending backlog | v0.6.2 close |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Pending backlog | v0.6.2 close |
| Todo (translator, examples) | citation-node-support-untracked | Pending backlog | v0.6.2 close |
| Todo (builder) | non-str-docname-typeerror-in-typstpdf-finish | Pending backlog | v0.6.2 close |
| Todo (typing) | modernize-typing-imports-drop-up006-up035-ignore | Pending backlog | v0.6.2 close |
| Todo (docs) | github-io-doc-links-404-missing-en-prefix | Pending backlog | v0.6.3 close |
| Todo (template_engine) | derive-typst-lang-duplicated-warning-block (review IN-01, Info) | Pending backlog | v0.6.3 close |
| Todo (docs) | docs-usage-installation-orphan-class | Pending backlog | v0.6.3 close |

## Session Continuity

Last session: 2026-07-25 — `/gsd-complete-milestone` v0.6.3
Stopped at: Milestone v0.6.3 closed and archived
Resume: `/gsd-new-milestone`

## Operator Next Steps

- Start the next milestone with `/gsd-new-milestone`.
