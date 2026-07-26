---
gsd_state_version: 1.0
milestone: v0.6.4
milestone_name: Read the Docs migration
current_phase: 30.1
current_phase_name: translations-repository-japanese-rtd-site
status: executing
stopped_at: Phase 30.1 gap closure planned (plans 07-11, waves 6-10)
last_updated: "2026-07-26T06:43:43.374Z"
last_activity: 2026-07-26
last_activity_desc: Phase 30.1 gap-closure round planned after verification scored 3/5
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 17
  completed_plans: 6
  percent: 17
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-25 at the v0.6.4 milestone start)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise. For v0.6.4 the same standard applies to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced.
**Current focus:** Phase 30.1 — translations-repository-japanese-rtd-site

## Current Position

Phase: 30.1 (translations-repository-japanese-rtd-site) — GAP CLOSURE, ready to execute
Plan: 7 of 11 (plans 01–06 executed; gap-closure plans 07–11 planned, waves 6–10)
Status: Ready to execute
Progress: [██░░░░░░░░] 17% (1/6 phases)
Last activity: 2026-07-26 — Phase 30.1 gap-closure round planned

**Phase 30.1 gap-closure notes (this round — plans 07–11):**

- **Why this round exists.** `30.1-VERIFICATION.md` scored **3/5**. SC#3 (submodule pin auto-advance) and SC#4/I18N-03 (glyph-correct ja PDF) are FAILED with machine-evidenced, reproducible defects; SC#2's visual half and D-03 check 4 are open owner observations. Both I18N-01 and I18N-03 stay `Pending` in REQUIREMENTS.md until this round closes.
- **The owner blocks twice**: Wave 6 (Plan 07 — flyout observation on both sites + the 発/単/釈 tofu look) and Wave 9 (Plan 10 — choosing the SC#4 fix option). Wave 9's option-b would change the English parent's PDF, i.e. reach into Phase 29's verified artifact, and needs explicit acceptance.
- **The owner's visual check runs BEFORE the pin advances, and that ordering is load-bearing.** Plan 06's page numbers (2, 3, 5, 6, 15, 21, 24) are properties of the 95-page artifact built from pin `dcc6a523`. Waves 7–8 move the pin and invalidate them. Plan 07 Task 1 pins artifact identity by SHA-256 before handing the owner a page list, and recomputes the sample if the SHA differs.
- **SC#3's root cause is settled, its fix is not yet proven.** `actions/checkout@v7` fetches the submodule by pinned SHA at `--depth=1`, so `refs/remotes/origin/<branch>` never exists and `git submodule update --remote` exits 128. Plan 08 resolves the branch at runtime from `.gitmodules` (not hardcoded) so the owed post-merge flip to `main` cannot re-break it. Everything downstream of the failing step — `decide`, commit, discard-header-churn — is **completely unexercised**; Plan 09 observes it for the first time.
- **SC#4's fix is deliberately unchosen at plan time.** Plan 10 measures (per-occurrence font + `/ToUnicode` attribution, RTD container font facts, the 95-vs-94 page delta, the English parent) and then presents option-a (ja manifest only) / option-b (English parent changes too) / option-c (accept + file a todo) / option-d (`typsphinx/` change — **unavailable**, milestone invariant #3). Plan 11 cannot start on an unmade decision.
- **`fontTools` is not a dependency and must not become one** — PDF forensics in Plans 10/11 use `pypdf` + stdlib only. Milestone invariant #1 (zero new runtime deps) is asserted per plan via `git diff -- pyproject.toml uv.lock`.

**Phase 30.1 execution notes (carry into execute/verify):**

- **CONTEXT.md provenance.** The Phase 30 discussion ran *before* D-15 split the phase, so the decisions live in `30-CONTEXT.md`. `30.1-CONTEXT.md` is a phase-scoped slice derived from it with the original D-NN identifiers preserved (D-01…D-10, D-12, D-15 — intentionally non-contiguous; D-11/D-13/D-14 are Phase 30's). If the two ever disagree, `30-CONTEXT.md` wins. D-12 is split across phases: its *removal* half is Phase 30's, its *arrival* half is 30.1's.
- **Waves 2 and 3 are `autonomous: false`** and block on owner RTD/GitHub web-UI action. The step most likely to be missed is linking the ja project under the **English parent's Settings → Translations** — without it you get two working but unswitchable sites.
- **The evidence file is `30.1-EVIDENCE.md`, not `30.1-VERIFICATION.md`** (planner decision PD-03). `{phase}-VERIFICATION.md` is a `/gsd-verify-work` reserved name and gets clobbered — this is the Phase 29 back-up-and-recombine problem, avoided by construction.
- **The submodule tracks `gsd/v0.6.4-read-the-docs-migration`, not `main`** (PD-02, overriding RESEARCH.md). Measured: `origin/main` has no `.readthedocs.yaml` and no `_resolve_language()`, so a `main`-tracking submodule pins a tree RTD refuses to build. This adds a **third** owed post-merge flip (parent Default branch, ja Default branch, `.gitmodules` `branch`) — recorded in Plan 04 `## Handoffs`.
- **`docs/locale/ja/`'s deletion belongs to Phase 30, not here** (PD-01). Consequence: this repository's catalogs and the translations repository's deliberately diverge from Plan 05 until Phase 30 lands. Do **not** "fix" it by regenerating catalogs here.
- **A green build proves nothing** (milestone invariant #7). SC#1 probes must target a full-coverage docname — `user_guide/builders` (65/65) or `examples/basic` (30/30). `changelog`, `contributing`, `api/index`, `user_guide/templates` are 0% translated and render all-English on a healthy site. `contributing.rst` is used deliberately as SC#3's *visible-delta* probe, which is a different use — do not conflate them.
- **A pin-bump run that only rewrote `POT-Creation-Date` does not satisfy SC#3**, which demands an observed run that moves the submodule pin.
- **13 `.mo` binaries are git-tracked here**, so the submodule checkout arrives with compiled catalogs already in place and `gettext_auto_build` would reuse them — shipping stale/English text on a green build. The ja manifest does `rm -rf` → `mkdir -p` → `cp -a` for this reason (threat `T-30.1-05`).
- `api-coverage.verify-pre` passes with `detected: false` and deliberately **no** `COVERAGE.md` — the validator rejects a row-less matrix, so a prose-only file would block the seal. Absent is the passing state. Keep RTD v3 API references phrased as one-off corroborating reads, never as an "integration".
- **Deletion guard.** `worktree.cleanup-wave` always blocks a branch containing deletions, no bypass. PD-01 keeps 30.1 deletion-free, so the one manual merge lands with Phase 30 rather than twice.

## Active Milestone: v0.6.4 — Read the Docs migration (Phases 29–33)

Move documentation hosting from GitHub Pages to Read the Docs so that every published URL resolves and
the downloadable PDF is the one `typstpdf` produced. 13 v1 requirements across 6 phases:

| Phase | Name | Requirements |
|-------|------|--------------|
| 29 | RTD Build Establishment (English Parent) + PDF Path Decision | RTD-01, RTD-02, RTD-03, RTD-04 |
| 30 | Hand-Rolled Multi-Language Machinery & Orphan Removal | I18N-02, DOC-08 |
| 30.1 | Translations Repository + Japanese RTD Site (INSERTED) | I18N-01, I18N-03 |
| 31 | Published-URL Cutover + Repo-Wide Link Guard | DOC-09, DOC-10, CI-05 |
| 32 | GitHub Pages Teardown (IRREVERSIBLE) | CI-04 |
| 33 | v0.6.4 Release Prep | REL-02 |

**Ordering is load-bearing, not cosmetic.** Every reversible action precedes the single action with no
undo. The roadmap deliberately **inverts** research's suggested order by putting the URL cutover
(Phase 31) *before* the Pages teardown (Phase 32), so the rewritten README/PyPI links are proven
against RTD while both hosts are still live. Phase 32 is kept standalone so the teardown has a standing
gate in front of it — its first criterion is a *freshly re-taken* observation that RTD is serving
English HTML, Japanese HTML, and the PDF-or-fallback, not a citation of earlier phases' evidence.

**The milestone's one genuinely open empirical unknown:** whether `typst.compile()` can reach
`packages.typst.org` from inside RTD's build sandbox (the four `@preview` packages must be fetched on a
cold cache; no documentation source resolves RTD's egress policy). The decision point is reading the raw
RTD build log in Phase 29, and the owner has pre-agreed the fallback — RTD-03's
`releases/latest/download/` link path — so Phase 29 cannot deadlock on it. The wheel question
(`manylinux2014_x86_64` confirmed on PyPI) and the font question (`typst-py`'s `embedded-fonts` feature
confirmed in `Cargo.toml`) are settled; do not re-open them.

**Two failure modes present as *successful builds*** and therefore have content-level criteria:
I18N-01 (a Japanese project builds green while rendering 100% English) and RTD-02 (Typst substitutes a
missing font silently, so a glyph-wrong PDF builds successfully). I18N-01's original cause —
`conf.py` reading only `SPHINX_LANGUAGE` — was closed by Phase 29's `_resolve_language()` seam, but
the failure mode outlives it: the ja catalogs are **24.3% translated** (257/1058 msgids, measured
2026-07-26), so Phase 30.1's probe must target a fully-translated docname (`user_guide/builders`
65/65, `examples/basic` 30/30) — `api/index`, `contributing`, `changelog` and
`user_guide/templates` are at zero and would read all-English on a healthy site.

**RTD-04 spans the milestone but is owned by Phase 29** (the failure mode is created at
project-creation time). Default Version stays `latest` throughout and flips to `stable` only after the
`v0.6.4` tag builds green. Phases 30–32 each re-fetch the documentation root as part of their own
verification so the middle of the milestone is not unowned.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 67 (55 through v0.6.2 + 12 in v0.6.3)
- v0.6.3: 6 phases / 12 plans / 28 tasks, 2026-07-23 → 2026-07-25
- v0.6.4: 0/5 phases, started 2026-07-25

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

Recent decisions affecting current work (full log in PROJECT.md Key Decisions):

- 2026-07-25 [v0.6.4 roadmap]: **URL cutover ordered before the Pages teardown**, inverting research's
  suggested order. The dependency is "RTD is green," not "Pages is gone" — rewriting while both hosts
  are live proves the new links resolve before anything is destroyed, and keeps the milestone's single
  no-undo action last among reversible work.

- 2026-07-25 [v0.6.4 roadmap]: **CI-04 kept as its own phase** rather than folded into a neighbour, so
  the irreversible teardown carries a standing gate — a freshly re-taken "RTD is serving en HTML, ja
  HTML, and the PDF-or-fallback" observation, not a citation of earlier evidence.

- 2026-07-25 [v0.6.4 roadmap]: **`sphinx-build -b linkcheck` is out of scope** (Future LNK-01). A
  repo-wide grep found zero `github.io` under `docs/source/`; the dead links live only in `README.md`
  and `pyproject.toml`, which linkcheck structurally never scans — a green linkcheck job would
  manufacture false confidence about exactly the bug class it was meant to prevent. CI-05 is a
  repo-wide real-HTTP check instead, and DOC-09 keeps its own separate fetch-based bar.

- 2026-07-25 [v0.6.3 close]: `examples/` templates joined the `@preview` version-sync guard. A bundled
  sample drifted three milestones behind unnoticed because the guard only watched the three
  extension-internal surfaces; a stale pin there is not cosmetic (it makes the sample fail to compile).

- 2026-07-25 [Phase 27.1]: explicit `typst_elements` precedence made **structural**, not incidental —
  auto-derived `lang` is pre-merged *under* the user's dict, and auto-derivation is gated to the
  bundled-default-template path so custom-template/`typst_package` users are never handed an
  undeclared kwarg.

- 2026-07-20: `branching_strategy: milestone` — ship unit is the milestone; the final phase is a
  prep-only Release phase, publish deferred to `/gsd-complete-milestone`. Push `main` to `origin` at
  every milestone close.

- 2026-07-22 [Phase 22.2]: dead-config sweep pattern — a config→output real-compile regression fixture
  (template `tests/test_package_only_config_gate.py`) is the bar, so registration-only asserts can't
  hide a dead feature. CONF-04/CONF-05 were the round-2 instances of the same defect class.

### Pending Todos

Nine open in `.planning/todos/pending/`. Three are now **promoted into v0.6.4** rather than deferred:

- **move-documentation-hosting-to-read-the-docs** (docs) — **promoted** → Phases 29–33.
- **github-io-doc-links-404-missing-en-prefix** (docs) — **promoted** → Phase 31 (DOC-09).
- **docs-usage-installation-orphan-class** (docs) — **promoted** → Phase 30 (DOC-08).

Still deferred:

- **add-sphinx-linkcheck-ci-job** (ci, docs) — stays open; deferred as Future requirement LNK-01 by
  owner decision 2026-07-25 (structurally blind to `README.md` / `pyproject.toml`). CI-05 covers the
  real failure class.

- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent;
  surfaced in Phase 22.2, permanent fix unplanned.

- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening, deferred
  from Phase 22.3 (D-06).

- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — deferred; do not "modernize" typing
  imports until this lands.

- **derive-typst-lang-duplicated-warning-block** (template_engine) — Phase 27.1 code review IN-01
  (Info), consciously waived.

Closed 2026-07-25: **verify-no-gap-between-pr98-and-phase25** (measured gap-free),
**examples-advanced-non-allowlisted-typst-elements-keys** (repaired at milestone close, see above),
and **close-pr98-after-v063-release** (posted + closed after the publish —
[comment](https://github.com/YuSabo90002/typsphinx/pull/98#issuecomment-5078139533)). The PR#98
close surfaced a process lesson: AlCalzone had asked an unanswered question in the thread
("would you rather like to have issues reported with the details instead?"), so the comment was
rewritten to answer it first (owner decision: **PRs are welcome**) rather than post a thank-you
over an open question. Read the whole thread before commenting on someone else's PR.

### Blockers/Concerns

**Open empirical unknown (v0.6.4, by design):** `@preview` package egress from RTD's build sandbox —
resolved in Phase 29 by reading the raw build log, with the owner's fallback (RTD-03) pre-agreed so the
phase cannot deadlock. Not a blocker; a decision point.

**Deletion guard, expected to fire in Phase 30:** `worktree.cleanup-wave` always blocks a branch that
contains deletions (no bypass). Phase 30 deletes the multilang machinery *and* the orphan doc pair, so
plan for a manual merge after measuring the deletion scope — Phase 27's precedent (PROJECT.md D-13).
Phase 30.1 also relocates `docs/locale/ja/`'s 13 catalogs out of this repository, which is a deletion
here as well.

**Eight owner-manual steps have no automated acceptance criterion** — seven RTD web-UI actions plus
creating the `typsphinx-doc-translations` GitHub repository (REQUIREMENTS.md § Owner-Manual Steps,
annotated with owning phases). The step most likely to be missed is linking the Japanese project under
the English parent's Settings → Translations — creating both projects without linking leaves two
working but *unswitchable* sites.

UI note: this project's phases are Typst PDF typesetting / config / docs / hosting work, **not**
frontend UI — the `ui.plan-gate` false-positives on PDF/HTML/template wording; use `--skip-ui` if it
flags a v0.6.4 phase. GATE-01 note (from v0.6.2, still standing): the honest-verifier rule — abstain to
`human_needed` rather than assert a truth without direct evidence.

**Recurring scoping lesson (v0.6.3, twice) — now milestone invariant #4:** a docs/config success
criterion phrased "anywhere under X" must be checked by a repo-wide grep at discovery time, not against
the files the requirement names. Phase 27 missed `docs/source/examples/*.rst` that way (closed
post-verify), and the `examples/` directory was missed by *both* Phase 26 and Phase 27 — surfacing only
at the milestone close as an unbuildable shipped sample. v0.6.4's Phase 30 deletion set is already known
to be **larger than the milestone brief stated** (research's grep added `_templates/page.html` and
`docs/Makefile`'s `multilang`/`serve-multilang` targets), which is itself the reason the invariant
demands a *fresh* grep rather than trust in any list — including research's.

### Roadmap Evolution

- Phase 30 edited: edited fields: title, goal, requirements, success_criteria, owner-manual dependencies, notes — I18N-01 split out to a forthcoming Phase 30.1; I18N-03 promoted to v1
- Phase 30.1 inserted after Phase 30: Translations Repository + Japanese RTD Site (URGENT)
- Phase 30.1 edited: edited fields: goal, depends_on (Phase 30 -> Phase 29, direction corrected), requirements (I18N-01, I18N-03), success_criteria (5 new), owner-manual dependencies, notes
- Phase 30 edited: edited fields: depends_on — added Phase 30.1 (deferred at the earlier edit because 30.1 did not yet exist and would have failed validation)

## Deferred Items

Items acknowledged and carried forward from milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |
| Config | CONF-06: `typst_elements` keys beyond papersize/fontsize/**lang** — `lang` は 2026-07-25 に CONF-07 として切り出し v1 昇格（Phase 27.1）、残りは据え置き | Deferred to future milestone | v0.6.3 scoping |
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

**Resume file:** .planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-CONTEXT.md

Last session: 2026-07-26T02:10:00.652Z
Stopped at: Phase 30 context gathered
Resume: `/gsd-plan-phase 29`

## Operator Next Steps

- Review `.planning/ROADMAP.md`'s v0.6.4 section — in particular the **RTD-04 ownership** note, the
  inverted teardown/URL-cutover ordering, and the two-bar link-verification split.

- **Confirm the RTD project slug** before Phase 29 executes — it is not self-service changeable and
  this milestone publishes it into every documentation link.

- Then plan the first phase: `/gsd-plan-phase 29`.
