---
gsd_state_version: 1.0
milestone: v0.6.3
milestone_name: config & docs 実測整合 + captioned tables
current_phase: 25
current_phase_name: captioned-table-figure-wrap-cross-references-reimplement-pr-
status: executing
stopped_at: Phase 25 planned
last_updated: "2026-07-23T14:58:51.028Z"
last_activity: 2026-07-23
last_activity_desc: Phase 25 execution started
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 3
  completed_plans: 1
  percent: 20
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-23 at v0.6.3 milestone start)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise.
**Current focus:** Phase 25 — captioned-table-figure-wrap-cross-references-reimplement-pr-

## Current Position

Phase: 25 (captioned-table-figure-wrap-cross-references-reimplement-pr-) — EXECUTING
Plan: 1 of 2
Status: Executing Phase 25
Last activity: 2026-07-23 — Phase 25 execution started

Progress: [░░░░░░░░░░] 0%

## Roadmap Summary (v0.6.3 — Phases 24–28)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 24 — Delete `typst_toctree_defaults` (dead-config sweep round 2, part B) | Remove the inert `typst_toctree_defaults` from every surface (registration, docs, examples, README, its test file) — pure grep-zero removal, 0-risk | CONF-05 |
| 25 — Captioned Table Figure Wrap + Cross-References (reimplement PR#98) | `.. table:: Caption` → `figure(table, caption, kind: table)` "Table N" + `:numref:`/`:ref:` `<label>`; caption-less stays plain; caption+width compose; 2nd-table stale-buffer fix | TBL-01, TBL-02 |
| 26 — `typst_elements` papersize/fontsize Pass-Through (dead-config sweep round 2, part A) | `typst_elements` `papersize`/`fontsize` reach `project()` (string vs. unquoted length); unknown key fails loud; copyright never leaks; `base.typ` byte-unchanged (Python-side fix only) | CONF-04 |
| 27 — Docs 実測整合 — Orphan Delete + Phantom Config Names | Delete orphan `docs/configuration.rst`; correct the 5 phantom config names in `user_guide/configuration.rst` (papersize/fontsize → working `typst_elements` examples) | DOC-06, DOC-07 |
| 28 — v0.6.3 Release Prep + Regression-Gate Close | Prep-only: bump `pyproject.toml` → 0.6.3 (sole literal) + `uv.lock` + `CHANGELOG` `[0.6.3]` + README Status; close on the full-corpus regression gate. Publish at `/gsd-complete-milestone` | (release/close — none) |

**Coverage:** 6/6 v1 requirements mapped (CONF-04, CONF-05, TBL-01, TBL-02, DOC-06, DOC-07) — no orphans, no duplicates, each to exactly one phase. Phase 28 carries no requirement (release/close).

**Ordering (research-driven, honored):** 24 (trivial 0-risk deletion) → 25 (translator captioned-table work, own state-machine risk) → 26 (`typst_elements` pass-through, own type-mismatch risk — **separate** phase from the table work per instruction) → 27 (docs cleanup — **must** follow 26 so phantom `papersize`/`fontsize` become *working* examples, not fatal ones) → 28 (release). TBL-01 before TBL-02 within Phase 25 (figure must exist to be labeled).

**Standing bar (GATE-01):** node-handler change (Phase 25) and config→output change (Phase 26) each ship a fail-pre-fix real `typst.compile()` regression fixture. Phase 25 MUST test a 2+-table document (stale-buffer bug invisible with one table) + caption+width + `:numref:`-resolves. Phase 26 MUST test papersize AND fontsize separately + a negative unknown-key case + a copyright-non-leak case. Pure-removal Phase 24 and docs-only Phase 27 carry no config→output change → grep-zero / grep-cross-check + green suite is the honest bar (no fixture).

**Milestone invariant (every phase):** zero new runtime deps, no `@preview` version bump — the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) stays untouched (CONF-04 is a 100% Python-side fix; `base.typ` byte-unchanged). Flag during planning if a phase needs otherwise (none expected).

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 28 is prep-only; the irreversible publish (tag `v0.6.3` → `release.yml` → PyPI + GitHub Release) executes at `/gsd-complete-milestone`.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 55 (through v0.6.2)
- v0.6.3 plans completed: 0 (roadmap just created)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Recent decisions affecting current work (full log in PROJECT.md Key Decisions):

- 2026-07-23: v0.6.3 roadmap created — Phases 24–28, derived from 6 v1 requirements (CONF-04/05, TBL-01/02, DOC-06/07). Numbering continues from v0.6.2's Phase 23. Shape follows research's dependency order: trivial deletion → captioned tables → `typst_elements` pass-through → docs cleanup → release. CONF-04 and TBL-01/02 kept in SEPARATE phases (distinct state-machine/type risks); docs phase strictly after CONF-04 (Pitfall 11).
- 2026-07-20: `branching_strategy: milestone` — ship unit is the milestone; the final phase is a prep-only Release phase, publish deferred to `/gsd-complete-milestone`. Push `main` to `origin` at every milestone close.
- 2026-07-22 [Phase 22.2]: dead-config sweep round 1 pattern — a config→output real-compile regression fixture (template `tests/test_package_only_config_gate.py`) is the bar so registration-only asserts can't hide a dead feature. CONF-04/CONF-05 are the round-2 (5th/6th) instances of the same defect class.

### Pending Todos

Backlog (`.planning/todos/pending/`) after v0.6.3 scoping — the dead-config sweep, PR#98 reimplementation, orphan-doc deletion, and phantom-config-name items were promoted into this milestone (Phases 24–27). Remaining pending:

- **move-documentation-hosting-to-read-the-docs** (docs) — RTD migration, out of this milestone; the github.io 404 doc-link fix is folded into it.
- **add-sphinx-linkcheck-ci-job** (ci, docs) — automate `sphinx-build -b linkcheck`; own ~1-phase task.
- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent; surfaced in Phase 22.2, permanent fix unplanned.
- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening, deferred from Phase 22.3 (D-06).
- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — deferred; do not "modernize" typing imports until this lands.
- **github-io-doc-links-404-missing-en-prefix** (docs) — folded into the RTD migration (owner decision 2026-07-23), not interim-fixed.

### Blockers/Concerns

None open. UI note: v0.6.3 phases are Typst PDF typesetting / config / docs work, NOT frontend UI — no `### UI hint` annotations added (the project's `ui.plan-gate` false-positives on PDF/rendering phases; use `--skip-ui` if it flags them). GATE-01 note (from v0.6.2): the honest-verifier rule — abstain to `human_needed` rather than assert a truth without direct evidence.

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |
| Config | CONF-06: `typst_elements` keys beyond papersize/fontsize (needs `base.typ` `project()` params) | Deferred to future milestone | v0.6.3 scoping |
| Todo (docs) | move-documentation-hosting-to-read-the-docs (+ github.io 404 links folded in) | Pending backlog | v0.6.2 close |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Pending backlog | v0.6.2 close |
| Todo (translator, examples) | citation-node-support-untracked | Pending backlog | v0.6.2 close |
| Todo (builder) | non-str-docname-typeerror-in-typstpdf-finish | Pending backlog | v0.6.2 close |
| Todo (typing) | modernize-typing-imports-drop-up006-up035-ignore | Pending backlog | v0.6.2 close |

## Session Continuity

**Resume file:** .planning/phases/25-captioned-table-figure-wrap-cross-references-reimplement-pr-/25-CONTEXT.md

Last session: 2026-07-23T14:06:05.691Z
Stopped at: Phase 25 context gathered
Resume: execute with `/gsd-execute-phase 24`

## Operator Next Steps

- Execute Phase 24 with `/gsd-execute-phase 24` (in progress via --chain auto-advance)
- Review the plan: `.planning/phases/24-delete-typst-toctree-defaults-dead-config-sweep-round-2-part/24-01-PLAN.md`
