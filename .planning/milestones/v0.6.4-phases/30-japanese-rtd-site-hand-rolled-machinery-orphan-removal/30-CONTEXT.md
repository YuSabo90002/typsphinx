# Phase 30: Japanese RTD Site + Hand-Rolled Machinery & Orphan Removal - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Japanese readers get typsphinx's documentation from Read the Docs as actual Japanese prose,
switchable through RTD's own flyout, and the repository stops carrying the hand-rolled
multi-language publishing machinery and the unreachable orphan docs it accumulated.

**Requirements:** I18N-01, I18N-02, DOC-08 — **plus I18N-03, promoted from Future to v1 during
this discussion (D-04).**

**⚠ This discussion changed the phase's shape. Read `<roadmap_amendments>` below before
planning.** The owner decided (D-06, reaffirmed after the cost was measured and presented) to
deliver the Japanese site from a **separate translations repository** built as an RTD
translation project, following the `sphinx-doc/sphinx-doc-translations` model — not by
re-importing this repository twice as the milestone brief and REQUIREMENTS.md Owner-Manual Step
2 assumed. That, plus the split into Phase 30 / 30.1 (D-15), makes several ROADMAP.md and
REQUIREMENTS.md statements stale. They are enumerated in `<roadmap_amendments>` and must be
amended before or during planning.

**Explicitly NOT this phase:** README / `pyproject.toml` / About URL rewrites and the repo-wide
link guard (Phase 31), the GitHub Pages *teardown* — disabling Pages and deleting the `gh-pages`
branch (Phase 32), the version bump and CHANGELOG (Phase 33). **No `typsphinx/` runtime code
change at all** (milestone invariant #3) — if the phase appears to need one, that is a re-scope
signal.

</domain>

<decisions>
## Implementation Decisions

> **2026-07-26 (plan-phase 30, dated annotation — not a silent overwrite):** D-01–D-10 and
> D-15 are tagged `[informational]` for Phase 30's decision-coverage gate. D-15's split
> assigned D-01–D-10 to Phase 30.1, which has since executed to completion (UAT passed,
> I18N-03 Complete); D-15 itself is realized structurally in ROADMAP.md. They remain locked
> decisions of record — the tag only marks them as not trackable against Phase 30's plans.
> Phase 30's own trackable decisions are D-11–D-14.

### Japanese PDF — the shared-manifest collision and its resolution

- **D-01 [informational]:** **The Japanese site ships a Japanese PDF.** Measured 2026-07-26: with the single
  shared `.readthedocs.yaml` (the original plan), `formats: [pdf]` and `build.jobs.build.pdf`
  apply to *both* RTD projects; the PDF job's `sphinx-build` carries no language flag, but
  `docs/source/conf.py:52`'s `_resolve_language()` reads `READTHEDOCS_LANGUAGE`, which RTD emits
  from the ja project's own Admin Language setting. So the ja project would emit a Japanese PDF
  whether or not anyone decided to. The owner chose to make that intentional rather than suppress
  it. **This decision is retained even after D-06 split the repositories** and made per-language
  manifests possible — it was re-confirmed on the new premise, not inherited by accident.
- **D-02 [informational]:** **Local feasibility is established, not assumed.** Measured 2026-07-26,
  `SPHINX_LANGUAGE=ja sphinx-build -b typstpdf docs/source <tmp>`: exit 0, **94 pages**,
  **1,811,337 bytes**, 2 warnings (en baseline: 93 pages / 1,678,961 bytes). Embedded fonts (9):
  `IPAexGothic`, `NotoSansCJKjp-Thin`, `DejaVuSansMono`, `DejaVuSansMono-Bold`, `Unifont`, and
  four Libertinus Serif variants. **1,997 CJK characters** extracted from the first 30 pages —
  real Japanese, not tofu. The first five fonts are host-provided; on RTD they must come from
  `build.apt_packages`.
- **D-03 [informational]:** **The ja PDF glyph gate is "content comparison against a local ja build + spot-check
  by eye."** Same shape as D-12 of Phase 29 but re-scaled, because all 94 ja pages are CJK so
  "the two affected pages" no longer means anything: build the same commit locally with
  `SPHINX_LANGUAGE=ja`, machine-check page-count equality, extracted-text equality, and CJK-font
  embedding; the human looks at a handful of sampled pages, not a fixed pair. **D-15 of Phase 29
  still governs the form**: run it by hand, paste the exact commands and output verbatim into the
  verification record, commit no comparison script (the RTD-built PDF is unreachable from CI, so
  a committed script would look like a gate that never runs).
- **D-04 [informational]:** **I18N-03 is promoted from Future to v1 and assigned to this phase (30.1).**
  REQUIREMENTS.md's `## Future Requirements` entry moves to `## v1 Requirements`, the
  Traceability table gains an `I18N-03 | Phase 30.1 | Pending` row, and the Deferred Items row in
  STATE.md is retired. Rationale: D-01 + D-03 *are* I18N-03's stated content (`build.apt_packages`
  font provisioning plus a gate proving the glyphs are right), so leaving it in Future would make
  the ledger describe work the phase is actually doing.
- **D-05 [informational]:** **Phase 29's D-11 is superseded, and its test's rationale with it.**
  `tests/test_readthedocs_config.py:262-280` asserts the sole PDF `sphinx-build` carries no
  locale/language flag, with a docstring justifying it as "not a step toward the deferred
  Japanese PDF (D-11)." The *assertion* stays true and useful (the language still arrives via env
  var, never a flag), but the *stated reason* is now false. Amend the docstring/message to cite
  D-04/D-05 of this phase; do not delete the assertion.

### Translations repository split (the phase's largest change)

- **D-06 [informational]:** **The Japanese documentation is built from a separate repository,
  `typsphinx-doc-translations`, registered as an RTD translation project of the `typsphinx`
  parent.** This follows the measured `sphinx-doc/sphinx-doc-translations` model, not the
  re-import-the-same-repo model that REQUIREMENTS.md Owner-Manual Step 2 describes.
  *Measured 2026-07-26 from RTD's public API:* `projects/sphinx/` has `language.code = "en"`,
  `translation_of = null`, `versioning_scheme = "multiple_versions_with_translations"`;
  `projects/sphinx/translations/` returns **15** projects (`sphinx-ar`, `sphinx-ja`, …), every one
  of them a distinct RTD project whose `repository.url` is
  `https://github.com/sphinx-doc/sphinx-doc-translations` — **not** `sphinx-doc/sphinx`.
  *Measured repository shape:* a `sphinx` git submodule pinned to `sphinx-doc/sphinx@master`, a
  `locales/` directory holding the catalogs, and a `.readthedocs.yml` with
  `sphinx.configuration: sphinx/doc/conf.py`, `submodules: {include: all}`,
  `build.jobs.post_create_environment: cp -a locales sphinx/doc/`, and an `install` job doing
  `pip install -e sphinx …`.
  **Two concerns were raised before this was locked and the owner reaffirmed the decision:**
  (a) it points away from I18N-02's literal goal — `build_multilang.py`'s 180 lines are replaced
  by a second repository plus submodule plus a catalog-sync workflow, so the machinery is
  relocated and arguably grown rather than removed; (b) it complicates REL-02, addressed by D-07.
- **D-07 [informational]:** **The translations repository is tagged in lockstep with the parent, so `/ja/stable/`
  is real.** RTD's `stable` resolves to the newest semver tag *in the repository that project
  builds*, so without a matching tag the ja project has no `stable`. Sphinx's own 15 translation
  projects sidestep this by running `default_version = master`; typsphinx does not, because
  REL-02 requires `/en/stable/` and `/ja/stable/` to serve the same released version. **Standing
  cost:** every release from now on pushes a tag to two repositories, and the
  `/gsd-complete-milestone` procedure must carry the second one (submodule bump → tag push).
- **D-08 [informational]:** **Submodule pin advancement is automated with a GitHub Actions workflow in the
  translations repository**, modelled on `sphinx-doc-translations`'s `main.yml`. **Do not copy
  that workflow literally** — measured 2026-07-26, it is Transifex-coupled end to end
  (`TX_TOKEN`, the `tx` CLI installed via curl, `locales/lock-translations.py`,
  `locales/generate_templates.sh`, `locales/update.sh`) and typsphinx has no Transifex. The
  typsphinx shape is the same skeleton minus Transifex: `git submodule update --remote` →
  regenerate `.pot` → `sphinx-intl update` → commit if changed. Without this the ja site silently
  serves translations of an old English source, because RTD checks out the submodule commit the
  translations repo has recorded.
- **D-09 [informational]:** **Slug: `typsphinx-doc-translations` for the repository, and the ja RTD project slug
  is not a decision.** Unlike the parent slug (Phase 29 D-01/D-02, which Phase 31 burns into
  README, `pyproject.toml`, and the About field), the ja project's slug never gets published —
  readers see `https://typsphinx.readthedocs.io/ja/latest/`, and the slug appears only in RTD's
  dashboard. Enter `typsphinx-ja` (measured 404 → unclaimed on 2026-07-25; also the form all 15
  Sphinx translation projects use). **If it is taken, pick any other free name and continue** —
  the D-02 "stop and consult the owner" rule does *not* extend here, because nothing downstream
  depends on the string. Phase 29's D-03 ("the ja slug belongs to Phase 30's discussion") is
  hereby closed as over-scoped.
- **D-10 [informational]:** **The URL language segment is `ja`, and it is not configurable.** RTD derives the path
  segment from the project's Admin Language setting using ISO 639-1 codes; `jp` is an ISO 3166
  *country* code and is not offered. It cannot be set from `.readthedocs.yaml` or `conf.py`. This
  matches what the repository already uses everywhere (`docs/locale/ja/`, `docs/Makefile`'s
  `-D language=ja`, the `conf.py` language seam). Recorded because the question was raised
  explicitly; there is nothing to decide.

### Deletion set

- **D-11:** **`docs/usage.rst` is deleted whole — nothing is salvaged.** Measured 2026-07-26: 606
  lines, living outside `docs/source/`, referenced by no toctree (`docs/source/index.rst`'s four
  toctrees list `installation`, `quickstart`, `user_guide/*`, `examples/*`, `api/index` — no
  `usage`), therefore absent from the built site today. Its `Continuous Integration` and
  `Build Commands Reference` sections have no counterpart under `docs/source/` and **will be
  lost** — accepted, on the same reasoning Phase 27 used for `docs/configuration.rst`: the file
  has not been touched since 2026-07-04 and most likely carries the same drift-from-implementation
  that made `configuration.rst` a liability rather than an asset. `docs/installation.rst` (213
  lines, root orphan) goes the same way; `docs/source/installation.rst` (76 lines, toctree-live)
  is untouched. **Milestone invariant #5:** `tests/test_documentation_usage.py` and
  `tests/test_documentation_installation.py` are deleted in the *same commit* as their subjects —
  both hard-assert those files exist, and this is the exact trap that reddened the suite in
  Phase 27.
- **D-12:** **`docs/Makefile`'s `gettext` / `locale-init` / `locale-update` move to the
  translations repository.** ROADMAP.md's Notes paragraph calls these three "unchanged," but that
  was written assuming `docs/locale/ja/` stays in this repository; under D-06 it does not, so
  `locale-init` / `locale-update` would write into a directory that no longer exists. Following
  the Sphinx model, `.pot` generation happens on the translations side via the submodule's source.
  All three targets leave `docs/Makefile`.
- **D-13:** **`docs/Makefile:31-33`'s `html-ja` target is deleted.** It appears on neither SC#3's
  token list nor ROADMAP's keep-list. Once `docs/locale/ja/` leaves this repository,
  `sphinx-build -b html -D language=ja` finds no catalogs and renders 100% English — a target that
  fails silently rather than loudly. Delete it in the same commit rather than leave a broken
  convenience.
- **D-14:** **`docs.yml`'s gh-pages deploy step is repointed, not removed.** Change
  `publish_dir: ./docs/_build/multilang` → `./docs/_build/html`. Deleting the step is Phase 32's
  work (CI-04) and the roadmap's irreversible-actions-last ordering should not be disturbed; a
  one-line repoint keeps the workflow internally consistent while the multilang tree disappears.
  In practice the step never fires with the interim value — `branching_strategy: milestone` means
  Phases 29–33 land on `main` together — but a workflow pointing at a nonexistent tree is not left
  in the tree.
- **`custom.css` (Claude's discretion, exercised):** measured — all 7 rules in
  `docs/source/_static/custom.css` are `.language-switcher` selectors, and `_static/` contains
  nothing else. So: delete `custom.css`, delete `conf.py`'s `html_css_files`, and delete
  `html_static_path` as well, since the now-empty `_static/` cannot be tracked by git and a
  `html_static_path` pointing at a missing directory makes Sphinx warn.

### Roadmap restructuring

- **D-15 [informational]:** **The work splits into Phase 30 and a new Phase 30.1**, following the v0.6.3
  Phase 27 / 27.1 precedent.
  - **Phase 30** — hand-rolled machinery removal and orphan removal (**I18N-02, DOC-08**):
    `build_multilang.py`, `tox.ini`'s `[testenv:docs-multilang]`, `language-switcher.html`,
    `page.html`, `custom.css` + its `conf.py` wiring, `html_context` / `html_sidebars`, the
    `docs/Makefile` targets per D-12/D-13, the `docs.yml` swap per D-14, and the orphan pair per
    D-11.
  - **Phase 30.1** — translations repository + Japanese site (**I18N-01, I18N-03**): create
    `typsphinx-doc-translations`, move `docs/locale/ja/`'s 13 `.po` catalogs into it, add its
    submodule + `.readthedocs.yaml` + pin-bump workflow, create and link the ja RTD project, and
    run the D-03 glyph gate.
  - **Ordering constraint:** Phase 30's deletions must not run ahead of Phase 30.1's replacement
    being confirmed working — the same "do not delete the old switcher before RTD's replacement is
    confirmed" dependency the roadmap already states for Phase 29→30. Planning should decide
    whether that means 30.1 executes first or the two interleave; the constraint, not the ordering,
    is what is locked here.

### Claude's Discretion

Planning and research may settle these without asking again:

- **SC#3's grep pass/fail rule.** Two measured false positives must not be counted as live
  references: (a) `tests/fixtures/confval_field_body_render_gate/index.rst:15`'s
  `.. confval:: html_sidebars` — an unrelated Sphinx-directive test fixture that must survive;
  (b) `tests/test_readthedocs_config.py`'s four `html_context["language"]` assertions
  (lines ~294-323), which are collateral of the deletion and get repointed at `module.language` /
  `_resolve_language()` rather than deleted (the same class of problem as D-05, and the same
  answer). `CHANGELOG.md` and `.planning/milestones/**` stay excluded by standing precedent
  (D-02 / D-10 of earlier phases).
- Exact shape of the translations repository's `.readthedocs.yaml`, its `post_create_environment`
  copy step, submodule path naming, and whether the ja manifest declares `formats: [pdf]` inline or
  mirrors the parent's structure.
- Exact trigger and step list of the D-08 pin-bump workflow (schedule vs `repository_dispatch` vs
  both).
- Which pages the D-03 human spot-check samples, and how the evidence is formatted in the
  verification record.
- Whether Furo's default sidebar (restored once `html_sidebars` is removed) needs any further
  `conf.py` adjustment.

### Folded Todos

- **`.planning/todos/pending/2026-07-25-docs-usage-installation-orphan-class.md`**
  (`resolves_phase: 30`) — folded and **resolved** by D-11. Its open question ("`docs/source/` に
  同等の内容が存在するか。存在するなら削除、しないなら移設") was measured during this discussion:
  no `usage` docname exists under `docs/source/`, two sections have no counterpart, and the owner
  chose deletion anyway. Close this todo when the deletion commit lands.
- **`.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md`**
  (`resolves_phase: 32`) — the milestone's originating todo. Its Phase-30 slice (retire
  `build_multilang.py`, `[testenv:docs-multilang]`, `language-switcher.html`, the `conf.py`
  language wiring; stand up the ja project) is covered by the decisions above. **The todo stays
  open** — its own `resolves_phase` targets the Pages teardown. Note that its recorded assumption
  "`docs/locale/ja/` の 13 個の `.po` はそのまま活きる" is now only half true: the catalogs live on,
  but in a different repository (D-06).

</decisions>

<roadmap_amendments>
## Roadmap / Requirements Amendments Owed

These statements are now stale. Planning must not treat them as authoritative.

| Where | Current text | Why stale | Owed change |
|---|---|---|---|
| `ROADMAP.md` § Phase 30 Requirements | `I18N-01, I18N-02, DOC-08` | I18N-03 promoted (D-04); work split (D-15) | Phase 30 → `I18N-02, DOC-08`; new Phase 30.1 → `I18N-01, I18N-03` |
| `ROADMAP.md` § Phase 30 Goal + SC 1–5 | Written for one phase, same-repo ja | D-06, D-15 | Re-split across 30 / 30.1; SC#1's `/ja/latest/` content check moves to 30.1 |
| `ROADMAP.md` § Phase 30 Notes | "`docs/locale/ja/**/*.po` (13 files) and `docs/Makefile`'s `gettext`/`locale-init`/`locale-update` targets are **unchanged**" | D-06 moves the catalogs out; D-12 moves the targets out | Rewrite both clauses |
| `ROADMAP.md` § Phase 30 Notes | "the `peaceiris/actions-gh-pages` **deploy** step itself is Phase 32's to delete, so its `publish_dir` must not be left pointing at a tree that no longer exists" | Still correct — D-14 satisfies it | No change; cite D-14 |
| `REQUIREMENTS.md` § Future Requirements → I18N-03 | "A Japanese PDF. Deferred…" | D-04 | Move to `## v1 Requirements`, § I18N |
| `REQUIREMENTS.md` § Owner-Manual Steps 2–4 | "Create a **separate** RTD project for Japanese — **re-import the same repository**" | D-06 builds from a *different* repository | Rewrite step 2; steps 3 (link under Translations) and 4 (activate versions independently) stand unchanged and are still the most-likely-missed steps |
| `REQUIREMENTS.md` § Traceability | 12 rows, no I18N-03 | D-04, D-15 | Add `I18N-03 | Phase 30.1`; re-map I18N-01 → 30.1; coverage 12 → 13 |
| `REQUIREMENTS.md` REL-02 | "`/en/stable/` and `/ja/stable/` serve that same released version" | Satisfiable only via D-07's two-repository tagging | Keep the bar; annotate with D-07's standing release cost |
| `STATE.md` § Deferred Items | I18N-03 row, "Deferred to Future" | D-04 | Retire the row, note promotion date 2026-07-26 |
| `PROJECT.md` § Current Milestone | "`docs/locale/ja/` の 13 個の `.po` はそのまま活きる"; "**日本語 PDF は出さない**" | D-06, D-01/D-04 | Both clauses reversed — record the reversal with its rationale, do not silently overwrite |

</roadmap_amendments>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints
- `.planning/ROADMAP.md` § "Phase 30" — the goal, five success criteria, owner-manual dependency
  list, and Notes paragraph. **Read together with `<roadmap_amendments>` above** — several
  statements are superseded.
- `.planning/REQUIREMENTS.md` — I18N-01 / I18N-02 / DOC-08 text and the I18N-03 Future entry
  (promoted, D-04); § "Milestone Invariants" (all seven — especially **#3** no `typsphinx/`
  change, **#4** repo-wide grep at discovery time, **#5** delete collateral tests in the same
  commit, **#7** a green build proves nothing about content); § "Owner-Manual Steps" items 2–4;
  § "Out of Scope".
- `.planning/PROJECT.md` § "Current Milestone: v0.6.4" — the four post-research owner decisions of
  2026-07-25, two of which this discussion reversed (see `<roadmap_amendments>`).
- `.planning/STATE.md` § "Accumulated Context" — the standing honest-verifier rule (abstain to
  `human_needed` rather than assert an unevidenced truth), the `ui.plan-gate` false-positive note
  (use `--skip-ui`), the expected `worktree.cleanup-wave` deletion-guard block, and the
  recurring "anywhere under X ⇒ repo-wide grep" scoping lesson.

### Prior phase context (do not re-derive)
- `.planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-CONTEXT.md` —
  D-01/D-02 (parent slug rules), D-04/D-05 (PDF output path and filename), D-10/D-11
  (`fonts-noto-cjk` rationale — **D-11 superseded here, see D-05**), D-12/D-13/D-14/D-15 (the
  PDF content-comparison gate whose form D-03 reuses).
- `.planning/phases/29-.../29-VERIFICATION.md` § "Phase 33 Handoff Precondition" — the two owner
  actions owed later (Default version `latest` → `stable` after the tag; Default branch back to
  `main` after the merge).
- `.planning/research/SUMMARY.md`, `STACK.md`, `ARCHITECTURE.md`, `PITFALLS.md` — note
  PITFALLS.md's "omit `formats:`" reading is **superseded**; STACK.md's is the one to build
  against.

### External models measured during this discussion
- RTD API — `https://readthedocs.org/api/v3/projects/sphinx/` and
  `.../projects/sphinx/translations/` — the empirical basis for D-06 (15 separate translation
  projects, all building `sphinx-doc/sphinx-doc-translations`).
- `https://github.com/sphinx-doc/sphinx-doc-translations` — `.gitmodules`, `.readthedocs.yml`,
  `.github/workflows/main.yml`. The structural model for D-06/D-08. **Its `main.yml` is
  Transifex-coupled and must not be copied literally.**

### Files this phase touches or measures
- `docs/build_multilang.py` (180 lines) — deleted. Its `sessionStorage` root-redirect script lives
  at `:86`.
- `docs/source/_templates/language-switcher.html`, `docs/source/_templates/page.html` — deleted.
- `docs/source/_static/custom.css` — deleted, with `conf.py`'s `html_css_files` and
  `html_static_path`.
- `docs/source/conf.py` — `:71-73` `html_css_files`, `:76-83` `html_context`, `:85-95`
  `html_sidebars` deleted. **`:51-57`'s `_resolve_language()` seam and `language` assignment stay
  — Phase 29 built them and both RTD projects depend on them.**
- `docs/Makefile` — `:15` `.PHONY`, `:31-33` `html-ja` (D-13), `:35-43` `multilang` /
  `serve-multilang`, and `:18-29` `gettext` / `locale-init` / `locale-update` (D-12).
- `tox.ini:78-84` — `[testenv:docs-multilang]` deleted. `docs-html` (`:53-60`) and `docs-pdf`
  (`:62-69`) stay and are the phase's green-build gates.
- `.github/workflows/docs.yml` — `:34-35` `docs-multilang` → `docs-html`; `:40-43` PDF-copy step
  deleted; `:49` artifact path; `:62` `publish_dir` per D-14. **`:65-71` the tag-time Release
  attachment and the `docs-pdf` regression gate stay.**
- `docs/usage.rst`, `docs/installation.rst`, `tests/test_documentation_usage.py`,
  `tests/test_documentation_installation.py` — deleted together (D-11).
- `tests/test_readthedocs_config.py` — `:262-280` docstring amendment (D-05), `~:294-323`
  `html_context` assertions repointed (Claude's discretion).
- `tests/fixtures/confval_field_body_render_gate/index.rst:15` — **must survive**; grep false
  positive.
- `docs/locale/ja/LC_MESSAGES/**` — 13 `.po` (+ `.mo`) moved to the translations repository (D-06).
- `.readthedocs.yaml` — the parent manifest; unchanged by this phase unless the ja manifest's
  shape requires a symmetry edit.

### Todos
- `.planning/todos/pending/2026-07-25-docs-usage-installation-orphan-class.md` — folded, resolved
  by D-11.
- `.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md` — folded
  partially; stays open until Phase 32.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`pypdf>=6.14,<7`** is already in `pyproject.toml`'s `dev` extra and does everything D-03 needs
  (page count, text extraction, `/BaseFont` enumeration) — verified again on 2026-07-26 against
  the ja build. No new dependency.
- **`docs/locale/ja/**/*.po`** — 13 catalogs, already wired through `locale_dirs = ["../locale/"]`
  with `gettext_compact = False`. They work; they are only changing address.
- **The `conf.py` language seam from Phase 29** (`READTHEDOCS_LANGUAGE` > `SPHINX_LANGUAGE` >
  `"en"`) is exactly the mechanism the ja project needs. Nothing new is required for language
  resolution.
- **`docs-html` / `docs-pdf` tox environments** survive the phase and are its green-build proof
  (ROADMAP SC#5).

### Established patterns
- **Orphan deletion, Phase 27 precedent** — measure toctree reachability, delete the file and its
  hard-asserting tests in one commit, verify with a full `pytest` run *after* the deletion (the
  run, not the commit, is the proof — ROADMAP SC#4).
- **Deletion guard** — `worktree.cleanup-wave` always blocks a branch containing deletions, with no
  bypass. This phase is deletion-heavy on both axes, so a manual merge after measuring the deletion
  scope is expected (Phase 27 precedent, PROJECT.md D-13).
- **Repo-wide grep at discovery time** (invariant #4) — the deletion set is already known to exceed
  the milestone brief's list: research added `_templates/page.html` and the `docs/Makefile`
  multilang targets, and this discussion added `html-ja`, `html_static_path`, and the
  `test_readthedocs_config.py` collateral. Re-grep freshly immediately before the deletion commit;
  do not trust any list, including this one.
- **Advisory-CI precedent (`drift.yml`, D-07 of Phase 5)** — relevant to Phase 31's link guard, not
  to this phase. Noted so planning does not conflate them.

### Integration points
- **RTD web UI (owner-manual, unassertable by any test):** create the ja project against the
  *translations* repository, set its Admin Language = Japanese (this, not `conf.py`, is what makes
  RTD emit `READTHEDOCS_LANGUAGE=ja`), **link it under the English parent's Settings →
  Translations** (the step most likely to be missed — two working but unswitchable sites
  otherwise), and activate its versions independently (translation projects inherit nothing).
- **`typsphinx-doc-translations` → `typsphinx`** via git submodule; RTD checks out the *recorded*
  commit, which is why D-08's pin-bump automation is load-bearing rather than convenience.
- **Release procedure → two repositories** (D-07): submodule bump + tag push in the translations
  repository alongside the parent's tag, permanently.

### Open question inherited from Phase 29 (measure, do not assume)
`build.apt_packages: [fonts-noto-cjk]` installed successfully on RTD, but the font Typst actually
embedded was `MSNUZX+HanaMinA` — no Noto-named font appeared in the RTD PDF at all. Whether that
apt package is load-bearing was never established. It mattered little for four CJK strings in the
English PDF; it matters a great deal for a 94-page Japanese one. **Measure it before the ja
manifest relies on it.**

</code_context>

<specifics>
## Specific Ideas

Measurements taken during this discussion — use as baseline, do not re-derive:

- **ja typstpdf build (2026-07-26, local):** `SPHINX_LANGUAGE=ja sphinx-build -b typstpdf
  docs/source <tmp>` → exit 0, 94 pages, 1,811,337 bytes, 2 warnings. 9 embedded fonts incl.
  `IPAexGothic` and `NotoSansCJKjp-Thin` (host-provided). 1,997 CJK characters extracted from the
  first 30 pages.
- **ja catalog coverage (2026-07-26): 257 / 1058 msgids translated = 24.3%.** Per file —
  `user_guide/builders.po` 65/65, `examples/advanced.po` 36/36, `examples/basic.po` 30/30,
  `examples/index.po` 9/9, `installation.po` 21/22, `quickstart.po` 19/20, `index.po` 21/27,
  `user_guide/index.po` 13/14, `user_guide/configuration.po` 43/62, and **four files at zero** —
  `api/index.po` 0/513, `contributing.po` 0/97, `changelog.po` 0/86,
  `user_guide/templates.po` 0/77.
  **Owner decision: ship at 24.3%.** I18N-01's bar is "actual Japanese prose is served," not
  "fully translated"; untranslated msgids fall back to English by Sphinx's normal behaviour.
  Translation work is explicitly *not* this phase's — see `<deferred>`.
  **Consequence for I18N-01's SC#1 probe:** it must target a *translated* docname. Probing
  `changelog`, `contributing`, `api/index`, or `user_guide/templates` would show 100% English on a
  perfectly healthy site. `user_guide/builders` (65/65) and `examples/basic` (30/30) are the safe
  probes.
- **RTD API, `sphinx` project (2026-07-26):** 15 translations, all separate projects, all building
  `sphinx-doc/sphinx-doc-translations`; `sphinx-ja` is `language.code=ja`, `translation_of=sphinx`.
  Slug convention across all 15 is `sphinx-<language-code>`.
- **`sphinx-doc-translations` repository shape (2026-07-26):** `.gitmodules` → submodule `sphinx`
  at `sphinx-doc/sphinx.git` branch `master`; `locales/`; `.readthedocs.yml` with
  `sphinx.configuration: sphinx/doc/conf.py`, `submodules: {include: all}`,
  `post_create_environment: cp -a locales sphinx/doc/`; `.github/workflows/main.yml` +
  `test-translations.yml`, both Transifex-driven.
- **Multilang token grep (2026-07-26, repo-wide, excluding `.git` / `.planning` / `CHANGELOG.md`):**
  `.github/workflows/docs.yml:35,42,43,49,62`; `docs/Makefile:15,35,36,40,43`;
  `docs/build_multilang.py:17,26,86`; `docs/source/_static/custom.css` (7 hits);
  `docs/source/_templates/language-switcher.html:2`; `docs/source/_templates/page.html:8`;
  `docs/source/conf.py:72,76,85,90`; `tox.ini:78,84`; plus the two false positives
  (`tests/test_readthedocs_config.py:289,299,307,315,323`;
  `tests/fixtures/confval_field_body_render_gate/index.rst:15`).
- **Orphan measurements (2026-07-26):** `docs/usage.rst` 606 lines, `docs/installation.rst` 213
  lines, `docs/source/installation.rst` 76 lines (toctree-live, untouched). No `usage` docname
  under `docs/source/`. `docs/source/index.rst`'s toctrees reference `installation`, `quickstart`,
  `user_guide/*`, `examples/*`, `api/index` only.

</specifics>

<deferred>
## Deferred Ideas

- **Raising ja catalog coverage above 24.3%** — roughly 285 msgids excluding the 513
  autodoc-generated `api/index` strings (`contributing` 97, `changelog` 86,
  `user_guide/templates` 77, plus ~25 scattered). Not this phase; belongs in its own scoped work
  once the ja site is live and the translation workflow is running. Worth filing as a Future
  requirement.
- **Retiring D-07's two-repository tagging** — if the release burden proves annoying, the
  alternative is Sphinx's `default_version = master` for the ja project plus a REL-02 rewording.
  Revisit after one or two releases, not now.
- **RTD Default Version `latest` → `stable` flip** — Phase 33's owner-manual handoff. Applies to
  the ja project too once D-07's lockstep tagging exists.
- **RTD Default branch back to `main`** — owed after the milestone merges (Phase 29 handoff).
- **PR preview builds (RTD-05)** — Future; one owner-side checkbox, no repo work.
- **Documentation for tags before `v0.6.4` (RTD-06)** — structurally impossible.
- **Browser-language auto-redirect at the documentation root** — accepted loss. Deleting
  `build_multilang.py` removes the `navigator.language` redirect and RTD has no equivalent (it
  redirects to a *version*, never auto-detects a *language*). A Japanese-browser visitor lands on
  English and clicks the flyout. Reimplementing it would re-add the template code I18N-02 exists
  to delete.

### Reviewed Todos (not folded)

- **`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`** — Phase 31 (DOC-09). This phase
  rewrites no published URL.
- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — stays open, deferred as Future LNK-01;
  structurally blind to `README.md` / `pyproject.toml` where the dead links actually live. CI-05
  (Phase 31) covers the real class.
- **`2026-07-22-citation-node-support-untracked.md`**,
  **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`**,
  **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`**,
  **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** — all require `typsphinx/`
  runtime changes, forbidden by milestone invariant #3.

</deferred>

---

*Phase: 30-Japanese RTD Site + Hand-Rolled Machinery & Orphan Removal*
*Context gathered: 2026-07-26*
