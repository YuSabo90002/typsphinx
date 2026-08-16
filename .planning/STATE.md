---
gsd_state_version: 1.0
milestone: v0.9.0
milestone_name: per-document templates
current_phase: 55
current_phase_name: v0.8.0-Derived Defects
status: planning
stopped_at: Phase 54.1 context gathered
last_updated: "2026-08-16T03:28:25.332Z"
last_activity: 2026-08-16
last_activity_desc: Phase 54.1 planned — 5 plans in 3 waves, plan-checker PASSED, 13/13 decisions and 2/2 requirements covered
progress:
  total_phases: 6
  completed_phases: 3
  total_plans: 22
  completed_plans: 22
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-15 at the v0.8.0 milestone close)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise. The same standard applies to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced. From v0.7.0 the standard extends again: the output must be *well typeset*, not merely correct.
**Current focus:** Phase 54.1 — bundle-directory-safety-templates-path-collision-refusal-and
Close WR-01 (the wholesale bundle copy can republish a project's Sphinx `templates_path` directory,
while the docs recommend exactly that layout) and CR-01 (the built-in `"typst"` key's CONF-17
violation is discovered only at `finish()`, after every `.typ` file is written). Context gathered
2026-08-16: refuse with `ExtensionError`, check in a pre-write pass at the top of `write()`, and fix
the `_templates/` recommendation across `docs/source/`, `README.md` and `examples/`.
Planned 2026-08-16: 5 plans in 3 waves. Three decisions were added at planning time — **D-11**
(`examples/charged-ieee/approach2/` gets the same `_templates/`→`_typst/` rename as D-09), **D-12**
(SC#2's grep gate polices `docs/source/` + `README.md` + `examples/` only; `tests/` is excluded,
measured basis: zero files under `tests/` set both `templates_path` and `typst_template`), and
**D-13** (the discovery-time grep found one hit D-08's floor missed —
`examples/advanced/_templates/custom.typ:5`, a comment inside the file D-09 moves).

Phase 54 (complete) context, retained for reference:
26/26 v1 requirements mapped, zero orphans. Every `typst_documents` entry gets to name its own
template through a validated `typst_document_templates` registry, and one output rule — every used
key's bundle copied wholesale to `<outdir>/_template/<key>/` — replaces `_write_template_file()`,
`_copy_template_directory()`'s `.typ` exclusion, `copy_template_assets()`'s three early returns and
`typst_template_assets`. Breaking on two axes: the `_template.typ` relocation and that removal.

v0.8.0 shipped 2026-08-15 (6 phases, 45 plans, 24/24 requirements, zero known gaps) and is archived;
its 12 deferred artifacts are in § Deferred Items below, five of which — XREF-05, BLD-07, BLD-08,
BLD-09, IMG-03 — are now **v0.9.0 requirements mapped to Phase 55** rather than open todos.

Next action: `/gsd-execute-phase 54.1`

## Current Position

Phase: 55 — v0.8.0-Derived Defects
Plan: Not started
Status: Ready to plan
Progress: [██████████] 100% (5/5 plans complete)
Last activity: 2026-08-16 — Phase 54.1 complete, transitioned to Phase 55

**Wave map:** W1 = `54.1-01` (WR-01 runtime tracer) + `54.1-02` (WR-01 docs half, two `git mv`
renames) · W2 = `54.1-03` (CR-01 hoisted CONF-17 + reserved-key case) + `54.1-04` (WR-01 edge/control
cases) · W3 = `54.1-05` (cross-kind aggregation, `Unreleased` CHANGELOG entry, phase-boundary green).

**Two execution hazards recorded at planning time:**

1. `54.1-02` deletes tracked paths (both renames are `git mv`). `worktree.cleanup-wave` blocks any
   branch containing deletions with **no bypass** — expected, not a failure. Verify the deletion
   scope is exactly `examples/advanced/_templates/custom.typ` and
   `examples/charged-ieee/approach2/source/_templates/_template.typ`, then merge that worktree
   branch by hand.

2. `54.1-03` and `54.1-04` share Wave 2 with disjoint `files_modified`, but `03` changes runtime
   refusal behaviour while `04` authors five new fixtures — a fixture with a template at its
   source-tree root would pass in `04`'s worktree and fail after merge. `54.1-04` carries two
   mechanical sweep assertions against exactly that.

**"Green" for this phase means green modulo exactly the 7 pre-existing
`tests/test_state_guard_shapes_gate.py` failures** (recorded in
`phases/53-template-registry-foundation/deferred-items.md`, predating Phase 53). They are not a
regression this phase causes; no executor should "fix" them or report them as new RED.

> **This carve-out is STALE as of 2026-08-16 (measured at the Phase 54.1 Wave 1 and Wave 2
> post-merge gates).** Those 7 failures no longer occur — they were fixed upstream of Phase 54.1's
> base commit. `uv run python -m pytest` on the merged tree is **1314 passed, 5 skipped, 0
> failed**, with `black --check .`, `ruff check .` and `mypy typsphinx/` all clean. Treat the
> phase-boundary bar as **unconditional zero failures**, not "zero modulo 7". Any executor that
> reports those 7 as an accepted baseline is reading a stale note. `WINDOWS.md` entry 7 still
> tracks the underlying archived-path reference and remains open.

## Active Milestone (v0.9.0 — per-document templates)

Full phase detail, binding constraints and success criteria: [`ROADMAP.md`](ROADMAP.md) §
"🚧 v0.9.0 — per-document templates (ACTIVE)". Requirements and traceability:
[`REQUIREMENTS.md`](REQUIREMENTS.md).

**Goal:** every `typst_documents` entry can use its own template, Typst Universe package and
template-function arguments, instead of one globally-configured template being applied to every
master.

**Six phases, executing 53 → 54 → 54.1 → 55 → 56 → 57:**

| Phase | Name | Requirements |
|-------|------|--------------|
| 53 | Template Registry Foundation | TPL-01, TPL-03, TPL-04, TPL-05, CONF-14..18 (9) |
| 54 | One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions | TPL-02, CONF-19, OUT-04..07, BLD-05, BLD-06 (8) |
| 54.1 | Bundle Directory Safety — `templates_path` Collision Refusal and Pre-Write Path Validation (INSERTED) | WR-01, CR-01 (2) |
| 55 | v0.8.0-Derived Defects | XREF-05, BLD-07, BLD-08, BLD-09, IMG-03 (5) |
| 56 | Per-Document Template Documentation | DOC-15, DOC-16, DOC-17 (3) |
| 57 | v0.9.0 Release Prep (prep-only) | REL-08 (1) |

**The one hard ordering constraint is 53 before 54.** Deleting `_write_template_file()` breaks 31
test files that assert the root `_template.typ`; Phase 53 therefore lands the registry plumbing
output-identically first, so the tree is green at the boundary and the layout change is isolated
from the plumbing change. Phase 55 has no functional dependency on 53/54 and is sequenced after them
only to avoid contending for `builder.py` and `writer.py`.

**Milestone branch:** `gsd/v0.9.0-per-document-templates` — the branch carrying every milestone
commit — is **not** on `origin`. Milestone invariant #5 is encoded as Phase 53's SC#5 — push it in
the first phase, evidenced by a completed CI run including the Windows and macOS lanes, produced by
`gh workflow run CI --ref <branch>` (ci.yml's push/PR triggers are scoped to `main`/`develop`, so
the push alone runs no CI). *(Corrected 2026-08-15 during Phase 53 planning: originally named
`gsd/v0.9.0-milestone`, a stale local branch measured at `aed773c9` with zero milestone commits.)*

**Owner decisions locked before roadmapping** (do not re-open at planning): `_template/` is reserved
wholesale, so `tests/fixtures/template_named_dir_master/` moves in Phase 54; the
`typst_template_assets` removal ships a `config-inited` handler that also detects `typst_authors` and
`typst_toctree_defaults` — this codebase's first use of `config-inited`; the bundle copy runs in
`finish()` off a write-time key accumulator; `_write_template_file()` is deleted, not adapted; and
`TemplateEngine.resolve_template()` is widened to return the resolved path.

## Shipped Milestone (v0.8.0 — archived)

**SHIPPED 2026-08-15.** Phase detail is archived at
`milestones/v0.8.0-ROADMAP.md`; requirements at `milestones/v0.8.0-REQUIREMENTS.md`; phase
directories at `milestones/v0.8.0-phases/`. The brief below is retained as scoped.

**Goal:** move the unit of composition from "one `.typ` shared by every master, with the include
decision baked in at write time" to "per-master wrapper files that publish their include edge set as
Typst `state`, plus template-less docname-named content files that emit state-guarded includes at the
toctree's own position" — cutting the single root B-1, B-2 and defect A all grow from.

**Six phases, executing 47 → 48 → 49 → 50 → 51 → 52:**

| Phase | Name | Requirements |
|-------|------|--------------|
| 47 | Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection | COMP-01..04, OUT-01..03, BLD-02..04 (10) |
| 48 | Compile-Time Cross-Reference Guard | XREF-03, XREF-04 (2) |
| 49 | Per-Master Include Graph with State-Guarded Includes | COMP-05..12 (8) |
| 50 | PR #131 Image Path Defects | IMG-01, IMG-02 (2) |
| 51 | Two-Layer Output Documentation | DOC-14 (1) |
| 52 | v0.8.0 Release Prep (prep-only) | REL-07 (1) |

**The one hard ordering constraint: 48 must land no later than 49.** Fixing the include graph turns a
currently-silent content omission into a hard `label ... does not exist in the document` compile
abort for any shared document referencing a target present in one master but not another. Shipping the
graph first produces builds that fail outright. These two phases are **not** independently
parallelizable, in either direction.

**Milestone invariant #5 is Phase 47's SC#5.** `gsd/v0.8.0-multi-master-composition` exists locally
with planning commits and has **not** been pushed. It reaches `origin` in Phase 47, not at the release
PR — the discipline that paid immediately in v0.7.1, and whose absence cost v0.7.0 two defects. This
milestone raises the stakes: the case-insensitive-filesystem collision gap (research Pitfall 5) is
structurally invisible on Linux-only local runs.

**Phase 52 is prep-only** — version bump, curated CHANGELOG, evidence, handoff checklist, zero
irreversible action. REL-07 closes at `/gsd-complete-milestone`, not in the phase.

**Five open questions are assigned, not mapped.** They carry no REQ-IDs and are not counted in
coverage: B-2's RED state, the CR-01 self-collision policy and the case-normalization scope close in
Phase 47; `translator.py:4291`'s nature closes in Phase 48; the `:numref:` project-wide-vs-per-wrapper
divergence closes in Phase 49, on a live two-master fixture — no compile error catches that one.

## Shipped Milestone (v0.7.1 — archived)

Full phase detail, success criteria, and decisions: [`milestones/v0.7.1-ROADMAP.md`](milestones/v0.7.1-ROADMAP.md)
and [`milestones/v0.7.1-REQUIREMENTS.md`](milestones/v0.7.1-REQUIREMENTS.md). Phase artifacts are
under `milestones/v0.7.1-phases/`. The MILESTONES.md entry carries the stats, the curated
accomplishments, and the release record.

**Shipped 2026-08-11.** 8 phases (43-46, incl. inserted 44.1, 44.2, 45.1, 45.2) - 43 plans -
122 tasks - **19/19** v1 requirements complete, **zero known gaps** - `override_closeout` (no
milestone audit; 12 open artifacts acknowledged, 5 of which were re-measured and found already
resolved - see Deferred Items). Timeline 2026-08-04 -> 2026-08-11 (8 days, 421 commits). Code delta
excluding `.planning/`: 125 files, +10,760 / -935 lines.

Research was deliberately skipped (owner decision 2026-08-04) - a maintenance round over
already-diagnosed defects, each carrying a file/line-level todo, with the one new-behaviour item
CONF-08 resolved by direct measurement of Sphinx 9.1.0's LaTeX builder - so this milestone has **no
`research/SUMMARY.md`**. Coverage grew from 11/11 at roadmap creation to 19/19 through four phase
insertions; the five owed user-visible CHANGELOG callouts (CONF-08, CONF-09, CONF-10, CONF-11,
CONF-12) were all delivered in Phase 46's curated `## [0.7.1]` entry, and QUA-04 correctly took none
(confined to the `dev` extra, D-19).

**Published 2026-08-11.** PR #132 merged to `main` (15/15 CI checks green) and `v0.7.1` tagged on
merge commit `48bf135`. Release run `31462027486`: `validate` OK -> `build` OK -> `publish-pypi` OK
(after owner approval of the `pypi` environment) -> `create-release` **OK**. PyPI `typsphinx 0.7.1`
is live (wheel 135,318 B + sdist 580,288 B). The GitHub Release `Release v0.7.1` carries all three
assets (`.whl`, `.tar.gz`, and the tag-time `typsphinx.pdf`, 2,436,561 B). Second-repository tag
done: `typsphinx-doc-translations` pin advanced `87f242a` -> `48bf135` by `update-pin.yml` run
`31462409929` (commit `cf7fa30`) and tagged `v0.7.1` there.

**REL-04 closed here, for the first time, on generated evidence.** It carried unmet from v0.7.0,
where run `30848860064`'s `create-release` failed at `uv: command not found` and the fix landed on
`main` but was never exercised. This close exercised it: `create-release` completed success, and the
published body was then *measured* - lines 1-77 byte-identical to
`scripts/extract_changelog_section.py 0.7.1`'s stdout (`diff` clean), zero `git log --pretty`
commit-dump lines. Milestone invariant #5 (push the branch from Phase 43, not at the release PR) also
paid: a Windows-only path-separator defect surfaced on a dispatched CI run during Phase 46 instead of
at the release PR, which is the exact failure mode that cost v0.7.0 two defects.

**Read the Docs `stable` measured live 2026-08-11 (`46-HANDOFF.md` item 5, both projects — owner
confirmed, then re-measured against RTD's unauthenticated public API and real fetches):** root
`https://typsphinx.readthedocs.io/` → `/en/stable/` (200); `en` `stable` identifier
**`48bf135428bb093a77a432d93d16088ce6930342`** — the v0.7.1 merge commit itself — and `ja`
(project slug `typsphinx-ja`) `stable` identifier **`cf7fa3085078c0c5cc7f6614e89ae042ec95efef`**,
the translations repo's own v0.7.1-tagged commit. Both versions `active: true` / `built: true`;
both pages report `0.7.1`; both PDFs served (`en` 2,449,231 B / `ja` 2,642,276 B, `application/pdf`).
No owner setting flips were needed — both Default Versions have been `stable` since the v0.6.4 close,
the fourth consecutive close at which none was required.

**`46-HANDOFF.md`'s seven-item publish checklist is now fully discharged; nothing is owed forward.**

**Not a frontend UI milestone** — no phase carried a UI hint. `ui.plan-gate` false-positives on
"table"/"render"/"page" wording here.

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
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 47 P10 | 35min | 3 tasks | 4 files |
| Phase 53 P05 | 40min | 3 tasks | 3 files |

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

- [Phase 47]: Milestone branch gsd/v0.8.0-multi-master-composition pushed to origin (no PR); CI run 31492380799 completed success including windows-latest/macos-latest lanes, discharging Phase 47 SC#5

- [Phase 48] D-07: ONE shared guard-string derivation point. `_label_existence_guard()` is the sole
  site that builds a `context`/`query` string; it never derives a label itself, taking only
  `_namespace_label()`'s output, so demand and supply sides cannot diverge. Four call sites; a fifth
  spelling is the drift class the decision exists to reject.

- [Phase 48] D-11 accepted at UAT: the per-reference compile-time `query()` costs **-2.37%** on a
  full corpus, against tiers fixed before the measurement — bottom tier, record only.

- [Phase 48] Owner accepted two named limits rather than hiding them: a coincidental
  docname/label-namespace collision can still link to the wrong document (todo filed,
  `48-REVIEW.md` WR-02), and an `:orphan:` target now degrades with zero diagnostic at any layer.

- [Phase 48] G-48-4 **option-a**: whole-document references are guarded only when they resolve onto
  a real `found_docs` member. The five Sphinx-generated virtual pages (`genindex`, `py-modindex`,
  `search`, and two `../` forms) have no PDF counterpart and stay dead links by explicit choice.

- [Phase 53] SC#2/SC#5 closed on measured evidence: all four configuration shapes plus TPL-04 byte-identical post-change; milestone branch pushed to origin with honest two-run CI history (Run 31875380355 failed on pre-existing test_state_guard_shapes_gate.py path defect unrelated to Phase 53, fixed by d1eff100, Run 31875707734 succeeded on all 12 jobs including windows-latest/macos-latest)

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

**Count as of 2026-08-07: 12 files in `.planning/todos/pending/`.** The newest is
`review-pr-131-absolute-image-uri-fix` (builder, tests, **major**), captured 2026-08-07. This one is
a *review* task, not a defect record: PR #131 from external contributor @christianwehe (opened
2026-08-05, fixes #130, +440/−10 over 8 files, `MERGEABLE`) has sat with **zero reviews and zero
comments**. It rehomes the absolute image `uri` that Sphinx's `ImageConverter`/`ImageDownloader`
writes, which today collapses `copy_image_files()`'s src and dest onto one path and aborts the Typst
compile. The todo carries the checks to run before merging — including re-measuring the
contributor's RED claim independently, and testing whether the new image bookkeeping repeats the
per-build-not-per-master flaw seen in the include-dedup ledger. Not mapped to a v0.7.1 requirement.

**Count as of 2026-08-10: 10 files in `.planning/todos/pending/`.**
`review-pr-131-absolute-image-uri-fix` moved to `todos/completed/` — the review was performed and
PR #131 merged. Its RED claim was re-measured independently (3 tests fail with `builder.py` alone
reverted to `main`, with the exact reported symptoms) and the full suite showed no regressions
(main 45F/776P → PR 45F/779P; **corrected 2026-08-11 (QUA-04, D-06):** the 45 are a fixable dependency
defect, not an unfixable environmental artifact — a generic-linux `uv` wheel binary at
`.venv/bin/uv` that NixOS cannot exec, shadowing the working nix-store `uv` for subprocess children,
closed by this milestone's Phase 45.2). This milestone carries **two** unrelated `exit 127` / "command
not found" causes and they must not be conflated: (a) the local `.venv/bin/uv` ELF mismatch just
described, closed by QUA-04, and (b) the `create-release` job's missing `astral-sh/setup-uv` step
(REL-04, lines 425/587 below), which remains open until a real tag push runs `create-release` to
completion.

The review filed **two new todos** against the code the PR introduced, both in
`TypstBuilder._track_image()` and best fixed together:
`rehomed-converted-image-collides-with-srcdir-images-dir` (builder, **major**) — a converted image
rehomed to `images/<basename>` collides with an ordinary source image genuinely at
`<srcdir>/images/<basename>`, so one is silently never copied and the other document renders the
wrong picture, with no warning; measured with a probe. Note this is also a *failure-mode*
regression: pre-PR the same project aborted the build loudly. And
`track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` (builder, **minor**) —
`relpath(uri, doctreedir)` returns `../`-prefixed paths for an absolute URI outside `doctreedir`,
so `copy_image_files()` writes outside `outdir` (or collapses `src == dest`, reproducing #130);
not reachable via stock Sphinx post-transforms, which all write under `<doctreedir>/images/`.

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

**[Phase 47] One open review Warning carried forward, doc-only: WR-02.**
`47-REVIEW.md` closes at `status: issues_found` with CR-01 and WR-01 both verified-closed and one
Warning left open. `tests/test_master_include_set_predicate_gate.py`'s module docstring (lines ~25-31)
still says the pre-fix RED is "recording ... as `xfail(strict=True)`", but commit `e422bfb` removed all
six `@pytest.mark.xfail` decorators when the 47-13 fix landed. **Re-measured 2026-08-12 at UAT close and
still live** — `grep -c '@pytest.mark.xfail'` returns `0` while the docstring claim stands. Two class
docstrings (`TestGhostEntryIncludeSetUnit`, `TestUnhashableDocnameIncludeSetUnit`) carry the milder
"lands as an xfail" variant of the same staleness. **Not a functional defect** — all 8 tests pass and
the verbatim RED transcripts remain correctly cited to `47-GAP2-RED-EVIDENCE.md`; the cost is a
maintainer searching for markers that no longer exist. Fix is a past-tense rewrite, suggested verbatim
in `47-REVIEW.md`.

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
- Phase 45.2 inserted after Phase 45: Local Toolchain Repair — tox-uv to tox-uv-bare (QUA-04); tox is non-functional locally (every env exits 127) and 13 test modules fail under the mandated outer uv run; one dependency name; coverage 18/18 -> 19/19; no CHANGELOG callout (URGENT)

- **2026-08-11** — v0.8.0 roadmap created: **Phases 47-52**, 24/24 v1 requirements mapped, zero
  orphans, zero duplicates. Derived from this milestone's own `REQUIREMENTS.md`;
  `research/SUMMARY.md`'s build order was adopted for its **sequence** but not its labels (it proposes
  "Phase 47.1 … 47.6", and in this project decimals are reserved for phases *inserted* mid-milestone).
  Three deliberate divergences from the suggested structure: **(a)** the BLD-02/03/04 collision work
  is folded **into** Phase 47 rather than run later, because the split is what creates the
  self-collision hazard — with target-as-path in the same phase, the common `("index", "index.typ")`
  config collides immediately, and deferring the guard would ship a phase whose most common
  configuration is silently wrong; **(b)** OUT-01..03 ride with Phase 47, because B-1's fix *is*
  "compute include paths from the wrapper's resolved location", the same computation OUT-01 changes;
  **(c)** COMP-12's full-corpus GATE-02 pass stays inside the composition phase, per PROJECT.md's
  explicit instruction to treat a convergence failure there as a design-level finding. Also recorded:
  `research/ARCHITECTURE.md` predates PROJECT.md's design decision and proposes a **flattened**
  wrapper-side include graph — measured, rejected (it breaks document-order interleaving) and
  superseded by the state-guarded form. Its file:line integration inventory remains authoritative;
  its build-order flattening proposal does not.

- **2026-08-11** — OUT-01 is recorded in the roadmap as a deliberate **reversal** of v0.7.1 Phase 44's
  D-05/D-06/D-07 (a path in a target rejected and truncated to its basename; a nested docname's output
  forced into its own directory). OUT-02 keeps the security half of the same guards. The precedent is
  Phase 44.2 reversing Phase 44's D-02 within v0.7.1 — the phase that owns OUT-01 must state the
  reversal so the executor does not treat the existing guard code as sacred.

- **2026-08-15** — v0.9.0 roadmap created: **Phases 53–57**, 26/26 v1 requirements mapped, zero
  orphans, zero duplicates. **REL-08 was added to `REQUIREMENTS.md` at roadmap creation** (v1 total
  25 → 26) as the release requirement of the prep-only final phase, mirroring v0.8.0's REL-07; it
  closes at `/gsd-complete-milestone`, not in Phase 57. `research/SUMMARY.md`'s seven-phase
  suggestion was adopted for its **sequence** but not its count: its steps 3–5 (layout, 31-file test
  migration, deletion of `_write_template_file()`) are one phase because they are one green
  boundary, and its step 6 (config cleanup) rides with them because Pitfall 5 requires the
  `config-inited` detection handler in the identical commit as the `add_config_value()` removal. The
  five v0.8.0-derived defects, which SUMMARY.md explicitly left to the roadmapper, became their own
  phase (55) rather than being distributed into the registry phases.

- **2026-08-15** — Both of `research/SUMMARY.md`'s "Open Decisions Carried Forward" were **already
  closed by owner decision** when the roadmap was written and are recorded as binding constraints,
  not planning questions: `_template/` reserved wholesale (with the `template_named_dir_master`
  fixture moving in Phase 54), and the `typst_template_assets` removal shipping a `config-inited`
  warning covering all three removed values. `research/ARCHITECTURE.md` §5 asks for an owner decision
  on the fixture collision — it has one; the alternative (a different reserved directory name) must
  not be re-derived at planning.

- Phase 54.1 inserted after Phase 54: Bundle Directory Safety — closes Phase 54 review findings WR-01 (templates_path collision republishes Jinja dir) and CR-01 (CONF-17 checked only at finish(), after full write) (URGENT)

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
| Todo (ci, release) | release-create-job-missing-uv-verify-end-to-end — REL-04's `create-release` job failed on the v0.7.0 tag push (`uv: command not found`); workflow fixed on `main`, release repaired by hand, but the automation is still unproven | **RESOLVED at the v0.7.1 close** — release run `31462027486`'s `create-release` completed success and the published body was measured byte-identical to the extractor's output. The record can be filed to `todos/completed/` | v0.7.0 close → closed v0.7.1 close |
| Verification | No `v0.7.1-MILESTONE-AUDIT.md` produced (owner accepted 2026-08-11: `init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, 17/19 requirements were already Complete, and the 2 remaining were the publish-gated REL rows the close itself discharges). Fourth consecutive `override_closeout` | Accepted at close | v0.7.1 close |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Acknowledged, deferred again — tracked as Future requirement LNK-01; `links.yml`'s repo-wide lychee check already covers the links this release adds (`46-HANDOFF.md` deferral #1) | v0.7.1 close |
| Todo (source) | modernize-typing-imports-drop-up006-up035-ignore | Acknowledged, deferred again, **doubly deliberate** — `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and the milestone's own binding constraint #6 forbade it (`46-HANDOFF.md` deferral #2) | v0.7.1 close |
| Todo (builder, tests) | duplicate-typst-documents-target-silently-drops-a-master | Acknowledged, deferred — **re-measured live in Phase 46 and still reachable**: two entries both targeting `manual.typ` make `-b typst` exit 0 with no collision warning and silently drop the first master's body, because Phase 44's guard compares only against `env.found_docs` and the reserved `_template`, never against already-resolved targets. A `typst_documents`-modelling defect, unrelated to release prep (`46-HANDOFF.md` deferral #4). **Named first among next-milestone candidates** | v0.7.1 close |
| Todo (builder, writer) | a-master-that-is-also-a-toctree-child-is-unrepresentable | Acknowledged, deferred — same `typst_documents`-modelling cluster (`46-HANDOFF.md` deferral #5) | v0.7.1 close |
| Todo (builder, writer) | shared-document-silently-dropped-from-all-but-first-master | Acknowledged, deferred — the include-dedup ledger is per-build, not per-master; same cluster (`46-HANDOFF.md` deferral #6) | v0.7.1 close |
| Todo (builder) | rehomed-converted-image-collides-with-srcdir-images-dir | Acknowledged, **ships in v0.7.1 unfixed by owner decision D-27** (major): a converted image rehomed to `images/<basename>` collides with a real source image at `<srcdir>/images/<basename>` — one is never copied, the other document renders the wrong picture, no warning. A **regression in failure mode**: the same project used to abort loudly. Entered the diff via the PR #131 merge; the prep-only fence forbade fixing it in Phase 46. No `### Known Limitations` CHANGELOG section and no GitHub issue, argued in full and declined | v0.7.1 close |
| Todo (builder) | track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri | Acknowledged, ships in v0.7.1 unfixed by owner decision D-27 (minor): `relpath(uri, doctreedir)` returns `../`-prefixed paths for an absolute URI outside `doctreedir`, so `copy_image_files()` writes outside `outdir` | v0.7.1 close |
| Todo (toolchain) | ruff-generic-linux-elf-unrunnable-on-nixos | Acknowledged, deferred — a `flake.nix`-side repair in the same family as QUA-04; `ruff` ships as a compiled Rust ELF that needs `nix-ld`, unlike pure-Python `black`/`mypy`. Does not block SC#3, which takes lint authority from CI (`46-HANDOFF.md` deferral #8) | v0.7.1 close |
| Seed (docs) | SEED-001-readme-quickstart-typst-documents-pdf | Dormant, but **substantially discharged** by CONF-08 (the default derivation) + DOC-11 (the Quick Start now documents `typst_documents`). Worth re-reading before promoting | v0.7.1 close |
| Seed (toolchain) | SEED-003-tox-dependency-groups-per-env — split the `dev` extra into PEP 735 `[dependency-groups]` so each tox environment installs only what it needs | Dormant; never scoped into v0.7.1 | v0.7.1 close |
| Deferred items (Phase 45.1) | Five test modules failing under `uv run sphinx-build` on NixOS (`test_examples_basic.py`, `test_integration_advanced.py`, `test_integration_basic.py`, `test_integration_multi_doc.py`, `test_integration_nested_toctree.py`, 45 failures total) | **RESOLVED, not deferred** — Phase 45.2 (QUA-04) fixed the root cause by renaming `tox-uv` → `tox-uv-bare`. Re-measured at the v0.7.1 close: `test_examples_basic.py` + `test_integration_basic.py` → 27 passed in 8.11s | Phase 45.1 → closed by Phase 45.2 |
| Todo (ci/docs) | 2026-07-22-add-sphinx-linkcheck-ci-job | Acknowledged, deferred — tracked as Future requirement LNK-01; `links.yml`'s repo-wide lychee check already covers the links each release adds | v0.8.0 close |
| Todo (source) | 2026-07-22-modernize-typing-imports-drop-up006-up035-ignore | Acknowledged, deferred **doubly deliberately** — `CLAUDE.md` independently instructs not to modernize typing imports until this todo lands, and v0.8.0's binding constraint #9 forbade it for the milestone | v0.8.0 close |
| Todo (ci/release) | 2026-08-04-release-create-job-missing-uv-verify-end-to-end | Acknowledged — REL-04's own record, **already closed at the v0.7.1 publish** (`create-release` success on run `31462027486`) and again at this close (run `31861043480`). `52-HANDOFF.md` flagged that this record may belong in `todos/completed/` rather than `pending/` and deliberately did not resolve it; it remains open for whoever next triages the ledger | v0.8.0 close |
| Todo (toolchain/nixos) | 2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos | Acknowledged, deferred — a `flake.nix`-side repair (Future requirement QUA-06); CI holds lint authority (D-08). **The cost landed this milestone**: an `I001` unsorted import block in `tests/test_builder.py` survived to a release-phase CI run because `ruff` has been unrunnable on this machine since Phase 45.2 | v0.8.0 close |
| Todo (translator) | 2026-08-12-label-collision-false-negative-in-compile-time-xref-guard | Acknowledged, **ships in v0.8.0 unfixed by owner decision D-01** (minor, NEW failure class created by Phase 48): two docnames sanitizing to the same label string (`a/b` and `a_u2f_b`) let a reference to the absent one render as a working link to the decoy instead of degrading to plain text | v0.8.0 close |
| Todo (builder) | 2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide | Acknowledged, ships in v0.8.0 unfixed by owner decision D-01 (minor, NEW failure class created by Phase 49): `make_include_edge_key` does not escape its own `#`/`>` separators, so a docname containing either can collide two edges | v0.8.0 close |
| Todo (builder) | 2026-08-14-unbounded-recursion-in-derive-master-edge-keys | Acknowledged, ships in v0.8.0 unfixed by owner decision D-01 (minor, NEW failure class created by Phase 49): an include chain deeper than Python's 1000-frame limit raises a raw `RecursionError` rather than a named `ExtensionError`. Sphinx's own 154-document `doc/` corpus does not reach it | v0.8.0 close |
| Todo (builder) | 2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide | Acknowledged, ships in v0.8.0 unfixed by owner decision D-01 (minor, NEW failure class created by Phase 50): the escape branch keys on `basename` while the collision branch keys on the full `rel_uri`, so two escaping absolute image URIs in different directories sharing a basename collide onto one key | v0.8.0 close |
| Todo (translator) | 2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures | Acknowledged, **excluded from every published surface by owner override D-07** — not documented as a limitation and not in the CHANGELOG. Classified as a bug for a later milestone to pick up, `resolves_phase: null` | v0.8.0 close |
| Todo (builder) | 2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows | Acknowledged, **product-side fix outstanding**. CPython 3.13 narrowed `ntpath.isabs()`, so `typsphinx/builder.py:910`'s bare `path.isabs()` silently skips the entire rehome/relocate/warn branch for a driveless-absolute Windows image URI; the sibling `_escapes_outdir()` already avoids the trap via `posixpath.isabs(stem) or _is_drive_qualified(stem)`. Plan 52-09 fixed only the **test-side** symptom to preserve Phase 52's zero-`typsphinx/`-lines fence, and filed this todo so the fact survives the test fix going green | v0.8.0 close |
| Seed (docs) | SEED-001-readme-quickstart-typst-documents-pdf | Dormant; substantially discharged by v0.7.1's CONF-08 + DOC-11, and v0.8.0's DOC-14 output-layout page addresses the adjacent confusion. Never scoped into v0.8.0 | v0.8.0 close |
| Seed (toolchain) | SEED-003-tox-dependency-groups-per-env | Dormant; never scoped into v0.8.0 (Future requirement QUA-07) | v0.8.0 close |

## Session Continuity

**Resume file:** .planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-CONTEXT.md
Archived milestone phases live under `.planning/milestones/v0.8.0-phases/` (and the equivalent
directory for each earlier milestone).

Last session: 2026-08-16T00:58:21.562Z
Stopped at: Phase 54.1 context gathered
Resume: `/gsd-plan-phase 53`.

**Nothing is owed forward from the publish.** All seven `52-HANDOFF.md` publish-checklist items are
discharged, including item 5 (Read the Docs `stable`), re-measured live 2026-08-15 through RTD's
unauthenticated public API and real PDF fetches on both projects. What IS owed forward is the
12-item Deferred Items ledger above — five of those are v0.8.0's own defects, four of which ship
unfixed by decision D-01 with no published surface other than that ledger and
`.planning/todos/pending/`.

## Operator Next Steps

- Plan the first phase with `/gsd-plan-phase 53`
- Phase 53 must push `gsd/v0.9.0-per-document-templates` to `origin` (milestone invariant #5) — the
  branch is local-only today, and CONF-18's reserved-device-name and case-collision cases are
  invisible to a local Linux-only run
