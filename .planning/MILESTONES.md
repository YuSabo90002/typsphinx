# Milestones: typsphinx

## v0.7.0 — API rendering design overhaul (Shipped: 2026-08-04)

**Closeout:** override_closeout — no `v0.7.0-MILESTONE-AUDIT.md` was run (owner decision at close:
`init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, and every
v1 requirement except the two publish-gated REL rows was already `Complete` before the close began).
6 open artifacts acknowledged as deferred (see STATE.md Deferred Items) — 4 of the 5 pending todos
are Phase 41 D-14's own recorded deferrals to v0.7.1+, one is a planning-docs hygiene record, and
the single dormant seed (SEED-001) was never scoped into this milestone.
**Phases:** 8 (36–42, incl. inserted 40.1) · **Plans:** 57 · **Tasks:** 158
**Requirements:** 32/33 v1 requirements complete · **Known gaps:** 1 (REL-04 — see below)
**Timeline:** 2026-07-29 → 2026-08-04 (7 days)
**Git:** milestone branch `gsd/v0.7.0-api-rendering-design-overhaul` (477 commits) merged to `main`; tagged `v0.7.0` on the merge commit
**Code delta (milestone scope, excl. `.planning/`):** 80 files, +14,619 / −339 lines. The runtime
change is concentrated in `typsphinx/translator.py` (the `desc_*`, `field_list`, admonition/rubric,
and citation handler families); the remainder is the RED-recorded regression gates each node-handler
change carries, the CHANGELOG-section extractor + `release.yml` rework, the version bump, and the
CHANGELOG entry.
**Released 2026-08-04:** PyPI `typsphinx 0.7.0` (wheel 122,514 B + sdist 477,342 B) published by
release run `30848860064` after owner approval of the `pypi` environment (15-minute wait timer).
GitHub Release `Release v0.7.0` carries all three assets (`.whl`, `.tar.gz`, and the tag-time
`typsphinx.pdf` from `docs.yml`) with the curated `## [0.7.0]` CHANGELOG body. Second-repository tag
done: `typsphinx-doc-translations` pin advanced to `75fd8ed` by `update-pin.yml` run `30848873442`
(commit `a2150b1f`) and tagged `v0.7.0` there. PR #129 merged to `main` with 15/15 CI checks green;
`v0.7.0` tagged on merge commit `75fd8ed`.

### Known Gaps

**REL-04 — not met; carried to v0.7.1.** The requirement is that the GitHub Release body is the
curated `## [X.Y.Z]` CHANGELOG section rather than a `git log --pretty` commit dump. The workflow
change landed correctly in Phase 41 (plan 41-01), but its **first real tag push failed**: the
`create-release` job runs `uv run python scripts/extract_changelog_section.py` and that job has no
`astral-sh/setup-uv` step — `validate` and `build` both do; `create-release` never needed uv until
REL-04 wired the extractor into it. Run `30848860064` went `validate` ✓ → `build` ✓ →
`publish-pypi` ✓ → `create-release` ✗ (`uv: command not found`, exit 127). `41-HANDOFF.md` item 1
had flagged this tag push as "the first moment that check exercises in anger"; it was, and it broke.

The v0.7.0 release body and the missing wheel/sdist assets were **repaired by hand** at the close, so
the published artifact matches what REL-04 describes. The automation has still never produced it.
`release.yml`'s `create-release` job gained the missing `Install uv` / `Set up Python` steps on
`main` after the release; REL-04 closes only when a real tag push exercises it end to end.

**Two CI-surface defects this milestone's own branch never saw until the release PR.** Alongside
REL-04, the Windows test lanes went RED on PR #129 — three signature render-gate modules added in
Phase 37 read and wrote `.typ` files with a bare `Path.read_text()`/`write_text()`, so Windows'
cp1252 default could not decode UTF-8 output (820 passed / 1 failed; Linux and macOS fully green).
Fixed in `9a544db` before merge. Both defects share a cause: **the milestone branch was never pushed
until the release PR**, so neither Windows CI nor a real tag push ran against it at any point during
the eight phases.

**Delivered:** API reference pages became readable. Autodoc/API output moved from a flat wall of
proportional bold text to a typeset reference document — monospace signatures with hanging-indent
wrapping, description bodies and field lists that indent by nesting depth off one shared constant,
and admonitions re-bucketed onto a taxonomy that survives greyscale. Citations gained full
round-trip support: a document containing one no longer fails the Typst compile outright. Zero new
runtime dependencies; the `@preview` package count stayed at four with no new version-lockstep site;
every node-handler change carries its own recorded-RED GATE-01 fixture.

**Key accomplishments:**

- **Signature typography (SIG-01..SIG-09, Phase 37)** — replaced `desc_signature`'s `strong({...})`
  wrapper with a composed `block(sticky: true, par(hanging-indent: 2.5em, …))`, routed every
  signature text run through `raw(...)` with ZWSP break-opportunity injection, and implemented the
  D-05 discriminator so names/annotations render bold monospace while each parameter renders italic
  and a resolved cross-reference keeps its hyperlink. Long signatures wrap without overflowing the
  margin and never split from the first line of their body across a page break — both proven by
  Typst-probe geometric render gates recorded RED against the untouched translator.
- **Structural indentation + info fields (IND-01..IND-05, FLD-01..FLD-03, Phase 38)** —
  `visit_desc_content` gained a real `pad(left: 2.5em, …)` body (no depth counter), `field_list`
  nests its own `SHARED_INDENT_STEP` pad inside it, and a single-value field body renders inline
  with its label. Field-body parameter names and types carry monospace treatment distinct from the
  plain-bold field label. The translator's last dummy-node delegation sites were replaced by one
  shared leaf-emission helper.
- **Admonition taxonomy + rubric nesting (ADM-01..ADM-06, Phases 36 & 39)** — all ten real
  admonition titles centralized on a single `sphinx.locale.admonitionlabels` lookup, five
  gentle-clues call sites re-routed, and the red family split into three pairwise-distinct functions
  after the owner reversed locked decision D-03 on a post-render greyscale probe. Phase 36 first
  decoupled the shared-emission seam so `desc_signature` and `rubric` could be restyled
  independently — with a recorded empty diff proving byte-identical `.typ` across the change.
- **Citations — full round trip (CIT-01..CIT-06, Phases 40 & 40.1)** — greenfield
  `visit_citation`/`depart_citation`/`visit_label` (run-scoped hanging-indent grid with
  back-reference markers) plus a guarded own-anchor addition to `visit_reference`. Phase 40.1 then
  hardened the degradation paths: `.. only::`-pruned citing sites fail closed instead of emitting a
  dangling `link()` target, ids-less `nodes.target` siblings no longer split one citation run into
  two independently-aligned grids, and the duplicated anchor-eligibility judgement collapsed into
  one shared predicate.
- **Two compile-fatal defects closed (MATH-02, TBL-03)** — `visit_math_block` now clears rather than
  arms the shared list-item separator flag (one blank line, not two, with a PDF-text invariance
  guard proving zero visible change), and `depart_table`'s `_emit_id_anchors` call moved past the
  `in_table` reset so a captioned table preceded by a standalone target emits both labels instead of
  aborting the compile on a dangling one. TBL-03 was promoted out of backlog item 999.2 on
  2026-08-03 *after* Phase 41 had already closed — the first requirement this project has added to
  an already-complete milestone.
- **Release notes sourced from the CHANGELOG (REL-04, Phase 41)** — a stdlib-only, positional
  `## [X.Y.Z]` extractor, pytest-covered and wired into both `release.yml` jobs, replacing the
  ~296-line `git log --pretty` dump. The same phase also converted every shell-context `${{ }}`
  interpolation in `release.yml` to `env:` passing (code-review CR-01), and left a standalone
  seven-item publish handoff checklist with zero irreversible action taken — the tag state was
  probed empty twice, 2m44s apart, to prove the fence held.
  **The extractor itself is correct and hand-verified; what failed at the real tag push is the job
  that calls it — see Known Gaps above.**

---

## v0.6.5 — inline-math separator hotfix (Shipped: 2026-07-29)

**Closeout:** override_closeout — no `v0.6.5-MILESTONE-AUDIT.md` was run (owner decision at close:
a 2-phase, 2-requirement hotfix where `init.manager` reported both phases `phase_complete=true` /
`verification_status=passed` and Phase 35's `35-RELEASE-EVIDENCE.md` had already discharged SC#1–SC#5
against live runs). 8 pending todos acknowledged as deferred (see STATE.md Deferred Items) — the 5
pre-existing ones were already named Out of Scope in the milestone's own REQUIREMENTS.md, and the 3
filed during v0.6.5 are its recorded deliberate deferrals (D-05, D-11) plus one docs-hygiene todo.
**Phases:** 2 (34–35) · **Plans:** 8 · **Tasks:** 27
**Requirements:** 2/2 v1 requirements complete (MATH-01, REL-03) · **Known gaps:** none
**Git:** milestone branch `gsd/v0.6.5-inline-math-separator-hotfix` (72 commits) merged to `main` via PR #125 (13/13 CI checks green before merge); tagged `v0.6.5` on merge commit `839d77f`
**Released 2026-07-28/29:** PyPI `typsphinx 0.6.5` (wheel 94,765 B + sdist 324,824 B, uploaded 21:15:39–21:15:40Z) + GitHub Release `v0.6.5` carrying all three assets (`.whl`, `.tar.gz`, and the tag-time `typsphinx.pdf` from `docs.yml`), via release run 30398631991 — green end-to-end after owner approval of the `pypi` environment. Second-repository tag done: `typsphinx-doc-translations` submodule pin advanced to `839d77f` by `update-pin.yml` run 30398664663 and tagged `v0.6.5` at `1891a09`. RTD `stable` rebuilt green on both tags and measured live: en `stable` identifier `839d77f38ffa`, ja `stable` identifier `1891a0905322`, root → `/en/stable/` (302→200), `/ja/stable/` 200, both pages reporting `0.6.5`, both PDFs served (en 1,705,336 B / ja 1,889,332 B). No owner flips were needed — both Default Versions were already `stable` from the v0.6.4 close.
**Known cosmetic cost (accepted, D-11):** the GitHub Release body is still the `git log` commit dump `release.yml` generates, not the curated `## [0.6.5]` CHANGELOG section — filed as `todos/pending/2026-07-29-release-notes-body-from-changelog-section.md`.
**Code delta (milestone scope, excl. `.planning/`):** 8 files, +560 / −4 lines — the entire runtime
change is +45 lines in `typsphinx/translator.py`; the rest is the GATE-01 regression fixture, the
version bump, and the CHANGELOG entry.

**Delivered:** A document mixing prose and math no longer aborts the Typst compile. Phase 34
root-caused the defect **by measurement** rather than from the backlog's guess, fixed it on both the
mitex and native emission paths, and pinned it with a real-`typst.compile()` fixture recorded RED
pre-fix; Phase 35 was prep-only, with zero irreversible action taken before this close.

**Key accomplishments:**

- Real-`typst.compile()` regression fixture reproducing the inline-math-after-text separator fatal in a list item, a collapsed confval field body, and a definition-list term, on both the mitex and native math paths, recorded RED against the unfixed translator
- Made `visit_math` participate in all three separator protocols (paragraph, code-mode concat, list-item) and `visit_math_block` participate in the list-item protocol, turning the GATE-01 gate GREEN on both the mitex and native `-D typst_use_mitex=0` emission paths
- Post-fix full regression sweep proves zero regression against Plan 01's pre-fix baseline (649 passed/1 skipped/0 failed), clean black/ruff/mypy, a fatal-free full-corpus GATE-02 pass, and a valid 93-page docs PDF — closing all five ROADMAP Phase 34 success criteria with direct evidence
- Added Construct G (labeled display-math inside a list item) to the GATE-01 fixture and four exact-string assertions derived from real `sphinx-build -b typstpdf` builds, closing all three test-side Warnings from the Phase 34 code review with zero `typsphinx/` changes.
- Filed two pending-todo records — WR-01's `visit_math_block` redundant blank line and `release.yml`'s release-notes-body rework — so both deliberate v0.6.5 deferrals (D-05/D-10, D-11) are recorded facts rather than lost ones.
- pyproject.toml/README.md/uv.lock all moved 0.6.4 -> 0.6.5 in lockstep; `uv.lock`'s diff is exactly one line (no transitive dependency re-resolved) and `typsphinx.__version__` confirms the editable-install metadata was regenerated.
- Inserted the curated `## [0.6.5]` CHANGELOG entry (lead paragraph + one-bullet Fixed + three-bullet Verified) and rolled over the tail link block, discharging ROADMAP Phase 35 SC#2 in both halves.
- Proved the post-bump v0.6.5 tree green across seven live runs (including both D-12 docs dogfooding builds), proved the three milestone invariants mechanically over the SHA-anchored full milestone diff (merge-base `eb696bb02d135227d880c679fc909513fe6f7d19`) with a positive control, proved no irreversible action was taken (empty local/remote tag checks plus an optional `gh release view` corroboration), and wrote the standalone six-item `35-HANDOFF.md` checklist `/gsd-complete-milestone` will execute — discharging ROADMAP Phase 35 SC#3, SC#4, and SC#5.

---

## v0.6.4 — Read the Docs migration (Shipped: 2026-07-28)

**Closeout:** verified_closeout — `v0.6.4-MILESTONE-AUDIT.md` passed (13/13 requirements, 6/6 phases
verified, integration checker all-wired, no broken flows); 5 pending todos acknowledged as deferred
(see STATE.md Deferred Items), 2 resolved todos filed to `todos/completed/`.
**Phases:** 6 (29–33, incl. inserted 30.1) · **Plans:** 33 · **Tasks:** 79
**Requirements:** 13/13 v1 requirements complete · **Known gaps:** none
**Git:** milestone branch `gsd/v0.6.4-read-the-docs-migration` (290 commits) merged to `main` via PR #124; tagged `v0.6.4`
**Released:** PyPI `typsphinx 0.6.4` (wheel + sdist) + GitHub Release `v0.6.4` (incl. the tag-time `typsphinx.pdf` asset — Phase 32's deferred live exercise proven), via release run 30309278708 (green end-to-end after owner approval of the `pypi` environment). RTD `stable` built green on the tag for both projects: root → `/en/stable/` 200, `/ja/stable/` 200 at the same release (en identifier `2bf6ef3`, ja at translations tag `v0.6.4`). Owner flips completed 2026-07-28: both Default branches → `main`, both Default Versions → `stable`; `.gitmodules` → `main`; Issue #119 closed; milestone branch deleted.
**Code delta (milestone scope, excl. `.planning/`):** 54 files, +900 / −7,118 lines — a net-negative
milestone: the hand-rolled multilang publishing machinery left the repository.

**Delivered:** Documentation hosting moved from GitHub Pages to Read the Docs end to end — English and
Japanese sites live behind RTD's own flyout, the downloadable PDF is the one `typstpdf` itself produced,
every published URL resolves, the hand-rolled multilang machinery is deleted, and the Pages host is
irreversibly torn down — with every reversible action ordered before the single no-undo one.

**Key accomplishments:**

1. **English RTD site stood up (Phase 29, RTD-01/RTD-04):** `.readthedocs.yaml` + the
   `READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"` `_resolve_language()` seam in `conf.py`; the raw
   build log proves typsphinx installed from the checked-out commit (not a stale PyPI wheel); the root
   URL owned at Default Version = `latest` with real-HTTP fetches re-taken by every later phase.

2. **RTD serves typstpdf's own PDF (Phase 29, RTD-02/RTD-03):** `formats: [pdf]` + a
   `build.jobs.build.pdf` override replaces RTD's LaTeX path; the milestone's one open unknown
   (`@preview` egress from RTD's sandbox) resolved to Branch A — the served PDF content-compared
   against the local `tox -e docs-pdf` baseline (93==93 pages, byte-identical text, CJK font present),
   so the `releases/latest/download/` fallback (RTD-03) was satisfied vacuously.

3. **Japanese site from a separate translations repository (Phase 30.1, I18N-01/I18N-03):**
   `typsphinx-doc-translations` created on the `sphinx-doc-translations` model (submodule pin
   auto-advanced by a repaired `update-pin.yml`, observed moving the pin end to end); `/ja/latest/`
   probed against 100%-translated docnames; the Japanese PDF's 10-NUL-byte glyph defect root-caused to
   Typst's font selection and fixed via a custom template's explicit
   `("Libertinus Serif", "Noto Serif CJK JP")` — owner visual UAT confirmed, no English regression.

4. **The deletion round (Phase 30, I18N-02/DOC-08):** `build_multilang.py`, the language switcher,
   its `conf.py` wiring, every task-runner target, the orphan `docs/usage.rst`/`docs/installation.rst`
   pair with 20 collateral tests, and the relocated `docs/locale/` tree — all gone on a green suite
   with the docs build warning-for-warning identical to baseline.

5. **URL cutover behind a proven guard (Phase 31, DOC-09/DOC-10/CI-05):** advisory lychee `links.yml`
   installed first and recorded red on the unfixed tree (negative control); then all 11 retired-host
   URLs in `README.md`/`pyproject.toml` rewritten and locked by a hermetic regression guard; all 35
   published URLs fetched over real HTTP; About → Website set and verified.

6. **Irreversible Pages teardown, gated (Phase 32, CI-04) + release prep (Phase 33, REL-02):** the
   teardown proceeded only behind freshly re-taken evidence that RTD was serving en HTML, ja HTML
   (1038 CJK chars content-verified) and both PDFs; `gh-pages` deleted with `ls-remote`-proven absence
   and the github.io 404 directly observed; version bumped to 0.6.4 with the CHANGELOG curated and the
   publish fence proven held (no tag, no PyPI state) until this close.

**Deferred:** 5 pending todos (sphinx-linkcheck CI job → Future LNK-01; citation-node support;
non-str-docname TypeError hardening; typing-import modernization; `derive_typst_lang()` warning-block
duplication) and 3 quality warnings from 30.1's review (contributing.rst toolchain-install step;
`custom_template.typ` as an unguarded fourth `@preview` lockstep site; no structural tests over the
live translations-repo manifests). Accepted losses (owner decisions 2026-07-25): no browser-language
auto-redirect at the root; old `github.io` URLs 404 with no redirect stubs. Standing cost: every
release now tags **two** repositories (parent + `typsphinx-doc-translations`).

**Archives:** `milestones/v0.6.4-ROADMAP.md`, `milestones/v0.6.4-REQUIREMENTS.md`,
`milestones/v0.6.4-MILESTONE-AUDIT.md`, phase artifacts under `milestones/v0.6.4-phases/`

---

## v0.6.3 config & docs measured fidelity + captioned tables (Shipped: 2026-07-25)

**Phases completed:** 6 phases, 12 plans, 28 tasks

**Key accomplishments:**

- Removed the registered-but-inert `typst_toctree_defaults` Sphinx config value from all seven code/doc/test surfaces (registration line, README, examples, surgically-edited docs/configuration.rst, deleted test file) while leaving the historical CHANGELOG.md entry untouched.
- Captioned `.. table::`/csv-table/list-table now renders as `figure(table(...), caption: {...}, kind: table)` with native "Table N" numbering and a single collision-free `<label>`, fixing both the stray-heading bug and the stale-buffer bug that silently dropped a 2nd table's caption.
- Real `sphinx-build -> typst.compile() -> pypdf` GATE-01 fixture proves the shipped Plan 25-01 translator fix compiles green end-to-end — every captioned-table caption survives exactly once (including the previously stale-buffer-lost 2nd table), `:numref:`/`:ref:` resolve with no duplicate/dangling-label fatal, and a durable fail-pre-fix proof reconstructs both original defect shapes from first principles.
- RawTypst marker + ELEMENTS_ALLOWLIST curated merge in `template_engine.py`, wired from `writer.py` as a separate argument -- `papersize`/`fontsize` now reach `map_parameters()` with correct per-key typing, an unknown key fails loud via `ExtensionError`, and `copyright` is structurally unreachable.
- Four standing real-`typst.compile()`/`sphinx-build` cases (papersize quoted, fontsize unquoted on a separate build, unknown-key abort, copyright non-leak) plus a durable `TestPreFixBasisFailureProof` reconstruction class prove CONF-04's `typst_elements` pass-through actually reaches `project()` -- with a recorded manual red->green confirmation against Plan 01's fix.
- Orphan `docs/configuration.rst` (489 lines, wrong package name `sphinxcontrib.typst`) deleted with its collateral test, the 5 phantom config names purged from `user_guide/configuration.rst` (papersize/fontsize rewritten as working `typst_elements` examples on top of CONF-04), and the redundant drifted config `list-table` removed from `api/index.rst` so config is documented in exactly one canonical place — with a scoped ja gettext regen that also fixed a latent docutils CJK-markup bug it activated.
- `base.typ`'s `project()` gains a `lang` parameter wired into `set text(lang:)`, driven by a new `derive_typst_lang()` conversion helper and a `uses_bundled_default_template()` provenance predicate that gates auto-derivation to the default-template path only, with explicit `typst_elements["lang"]` always winning.
- `lang` documented as the third `typst_elements` key in configuration.rst (derivation, default-template-only scope, explicit-wins precedence, zh_TW limitation) with a scope-limited ja gettext regeneration that keeps all 12 pre-existing obsolete catalog blocks intact.
- A new `tests/test_typst_lang_gate.py` (18 tests, 8 classes) with seven real-compile fixture projects proves CONF-07's `lang` typesetting parameter actually reaches the compiled PDF and changes Typst's generated figure/table supplement labels — via the D-07 split proof (font-independent `ja` source assertion + `de` pypdf-extraction linkage assertion with a new NBSP-tolerant matcher) — while three non-regression fixtures prove no non-default template path ever receives an injected argument it never declared, and a durable pre-fix-basis reconstruction plus a manually recorded red-to-green transition close the loop.
- Atomic version bump across pyproject.toml, uv.lock, and README.md's Status line, with the editable-dist install metadata refreshed so `typsphinx.__version__` reports 0.6.3 and all three version-sync guard tests stay green.
- Live re-ran the SC#3 full-corpus regression gate, full pytest suite, and both docs-build tox environments against the post-version-bump v0.6.3 tree, and recorded verbatim evidence plus SC#4/SC#5 git-diff assertions in a new `28-VERIFICATION.md`.
- Curated `## [0.6.3]` CHANGELOG entry (5 bullets, 6/7 v1 ledger IDs, BREAKING exactly on CONF-04/CONF-05) plus an advanced link-reference block, single source for the eventual GitHub Release body.

**Fixed at the close, before the tag:** the bundled `examples/advanced` sample was unbuildable on two
independent axes — five `typst_elements` keys outside the CONF-04 allowlist Phase 26 had just made
fail-loud, and `_templates/custom.typ` three milestones behind on its `@preview` pins
(`unknown variable: kai`). The template now declares `papersize`/`fontsize`/`lang` in its `project()`,
and `tests/test_preview_version_sync.py` gained a fourth-surface check over `examples/**/*.typ`.

**Closeout type:** `override_closeout`. All 6 phases were `phase_complete` with
`verification_status: passed` and 7/7 v1 requirements checked off, but no `v0.6.3-MILESTONE-AUDIT.md`
was produced (owner accepted at close — Phase 28's live re-run of the full-corpus gate, the full
pytest suite, and both docs-build environments stands in). Known verification overrides: 9 deferred
pending todos (see STATE.md Deferred Items).

**Verified at close:** full suite 657 passed / 1 skipped; `black`/`ruff`/`mypy` clean; full-corpus
regression gate fatal-free with an empty `unknown_visit` catalogue; `sphinx-build -b typstpdf
examples/advanced` builds. Zero new runtime dependencies; no `@preview` version bump.

---

## v0.6.2 rendering fidelity round 2 (Shipped: 2026-07-23)

**Closeout:** override_closeout (pre-close artifact audit surfaced one non-blocking item — Phase 22.3's verification abstained to `human_needed` for a single `verification: backstop` truth: exercising the two GATE-01 fixtures under a real `pytest-xdist` parallel run, which the project does not depend on. All five ROADMAP success criteria for 22.3 were independently verified with direct evidence, including two live revert-and-restore reproductions of the pre-fix defects. Every other phase (19, 20, 21, 22, 22.1, 22.2, 22.4, 23) is `phase_complete` + verification `passed`. Operator acknowledged the backstop item plus 9 pending-todo backlog entries as deferred at close — see STATE.md Deferred Items. **Known verification overrides: 1** (Phase 22.3 pytest-xdist backstop).)
**Phases:** 9 (19, 20, 21, 22, 22.1, 22.2, 22.3, 22.4, 23) · **Plans:** 30 · **Tasks:** 65
**Requirements:** 25/25 v1 requirements complete (FID-02..FID-14, PDF-01, PDF-02, CONF-01..CONF-03, WR-01, WR-02, DOC-01..DOC-05) · **Known gaps:** none milestone-blocking
**Git:** milestone work on `gsd/v0.6.2-rendering-fidelity-round-2` (branching strategy `milestone`); tagged `v0.6.2` at close
**Milestone invariant held:** zero new runtime dependencies, no `@preview` version bump, the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) untouched

**Delivered:** Round 2 of rendering fidelity — resolved the 13 medium/low silent mis-render findings the v0.6.1 audit left open as one coherent `translator.py` fix series grouped by root cause (clusters A–F), each pinned by a fail-pre-fix real-`typst.compile()` GATE-01 fixture, plus five inserted builder/config/docs phases: the Issue #117 `typstpdf` target-name PDF fix, nested-master compile-root alignment, a dead-config sweep that also repaired the entirely-broken `typst_package` Typst-Universe path end-to-end, builder-warning hardening (a missing/malformed master now fails loudly instead of a silent successful build), and a full-text README/CLAUDE.md accuracy pass. Closed on the full ~684-page Sphinx `doc/` corpus regression gate (fatal-free, valid `%PDF`, `unknown_visit` catalogue empty).

**Key accomplishments:**

- **Block-separation cluster (Phase 19, FID-02..FID-06):** adjacent block / sibling elements — paragraphs-in-list-items, sibling `desc_signature`s, rubric/option headings, definition-list term↔definition, back-to-back body-less `confval`s — now render with the visible separation the `-b html` authority shows instead of concatenating, via a coherent set of `parbreak()`/`linebreak()`/`terms(separator:)` separator fixes.
- **Signature token spacing + residual fidelity (Phases 20–21, FID-07..FID-14):** intra-signature token spacing restored (`class `/`exception ` prefix, C/C++ inter-token spaces, `:type:`/`:default:` colon-space) by reducing `desc_sig_space` to pass-through; long inline-literal runs wrap at UAX14 boundaries instead of clipping, paragraph soft-newlines collapse to a space, the codly config wrapper stops leaking as prose, external links get `show link:` styling, and PEP 3102/570 separators stop injecting their hover-title text inline.
- **Issue #117 target-name PDF fix + nested-master alignment (Phases 22, 22.1, PDF-01/PDF-02):** a single guarded `TypstBuilder._resolve_output_stem()` now governs all three `.typ`/`.pdf` output-path sites so `typst_documents = [('index', 'manual.typ', …)]` emits `manual.pdf`, not `index.pdf`; `TypstPDFBuilder.finish()` compiles each master's own on-disk `.typ` at its real docname-derived location so nested masters (`api/index`) resolve their `#include()`s and images — the compile basis now matches the translator's emission basis.
- **Dead-config sweep + `typst_package` repair (Phase 22.2, CONF-01..CONF-03):** deleted `typst_output_dir` and `typst_author_params` from every surface, and made the Typst-Universe `typst_package` path — previously unable to compile at all — work end-to-end (BUG-A `_template.typ` never written, BUG-B unconditional param injection, BUG-C dead author wiring, BUG-D wrong docs examples), all locked by a standing config→output regression gate so a registration-only assert can no longer hide a dead feature.
- **Builder-warning hardening + docs accuracy (Phases 22.3, 22.4, WR-01/WR-02, DOC-01..DOC-05):** a missing or malformed master now joins the aggregate `ExtensionError` instead of a silent successful build, the render gate stops asserting on `typst-py`'s uncontracted error wording, and README/CLAUDE.md/pyproject comments were re-derived from measured behavior — unverifiable numeric claims (test count, coverage %) removed rather than re-measured, with a `README`↔`pyproject` version-sync ratchet test added.
- **Release prep + regression-gate close (Phase 23):** bumped `pyproject.toml` → 0.6.2 (sole literal) with `uv.lock` in lockstep, curated the `## [0.6.2]` CHANGELOG entry covering all 25 ledger IDs (Issue #117 presented as a user-visible output-filename change; `### Removed` for the config deletions), and closed on a live full-corpus `-b typstpdf` gate.

---

## v0.6.1 rendering fidelity (Shipped: 2026-07-19)

**Closeout:** override_closeout (pre-close artifact audit clear; Phase 16 & 18 verified `passed`; Phase 17 — a pure audit/documentation phase — has no machine `VERIFICATION.md`, so `init.manager` could not certify `verified_closeout`. Its verification was instead the human confirmation gate 17-03 (D-01a: 14 accepted / 1 rejected of the 15 candidate findings, final severities signed off) plus `17-VALIDATION.md` (five mechanical consistency checks PASS), and its output — FID-01a — was proven downstream by Phase 18's real-compile regression fixture + the closing full-corpus gate. Verification override accepted by operator at close.)
**Phases:** 3 (16–18) · **Plans:** 9 · **Tasks:** 18
**Requirements:** 6/6 v1 requirements complete (TODO-01, MAN-01, LEN-01, AUD-01, FID-01→FID-01a, GATE-03) · **Known gaps:** none (13 medium/low audit findings recorded in `17-AUDIT-CATALOGUE.md` as a Future-Requirements pointer, not milestone-blocking)
**Git:** milestone work on `main` (branching strategy `none`), commits from `dcd03eb` (2026-07-13) through `cc7c64a` (2026-07-19); tagged `v0.6.1`
**Code delta (milestone scope):** ~15 source/test files, +1229 / −13 lines (`typsphinx/translator.py` + `tests/`); zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched

**Delivered:** Moved `typstpdf` output from "compiles fatal-free" (v0.6.0) to "renders faithfully" — implemented the last two silently-dropped nodes (`todo_node`, `manpage`), generalized the CSS-length converter into one shared helper (LEN-01), ran a full 151/151-docname human-assisted visual audit of the Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` baseline (15 findings catalogued, human-confirmed), fixed the sole high-severity finding (F12 wide-table overflow → FID-01a) with a real-compile regression fixture, and closed on the full ~684-page corpus regression gate (fatal-free, `unknown_visit` catalogue empty).

**Key accomplishments:**

- `.. todo::` now renders as a gentle-clues `task()` box with its own dynamic title, gated on `todo_include_todos` via `nodes.SkipNode` exactly like every official Sphinx builder — proven through a real `sphinx-build -> typst.compile() -> pypdf` round trip in both the enabled and disabled configurations.
- `visit_manpage`/`depart_manpage` delegate wholesale to `visit_emphasis`/`depart_emphasis`, rendering `:manpage:` page-reference text (e.g. `ls(1)`) italic in every separator/mode context, proven by a real `typst.compile()` + pypdf GATE-01 fixture spanning a paragraph, a list item, and a figure caption.
- Wired `_convert_length_to_typst` into `visit_figure`/`depart_figure` (`:figwidth:`) and `depart_table` (`:width:`, covering `.. table::`/`.. csv-table::`/`.. list-table::`), closing LEN-01 as the single shared CSS-length -> Typst-length helper used at every length-bearing docutils site.
- Built the rendering-fidelity audit scaffold — three same-corpus baselines (typstpdf/html/text), a corrected exact docname-to-page mapping for all 151 docnames, and the committed `17-AUDIT-CATALOGUE.md` skeleton with fresh provenance, so Plan 17-02's page-by-page visual pass can start immediately.
- Full 151/151-docname visual audit of the sphinx-doc/sphinx v9.1.0 corpus PDF vs. its `-b html` baseline complete, yielding 15 classified systemic findings (1 high / 12 medium / 2 low severity) ready for the Plan 17-03 human confirmation gate.
- Grouped the human-confirmed catalogue's single high-severity finding (F12, wide-table overflow) into `FID-01a`, appended it plus a medium/low pointer to REQUIREMENTS.md, and passed all five mechanical consistency checks against a freshly rebuilt corpus.
- depart_table now emits fr-weighted `columns: (Nfr, ...)` from docutils colwidth, and visit_literal injects U+200B after `.`/`_` in in-table raw() content, closing the audit's sole high-severity wide-table collision bug.
- Re-ran the real ~684-page Sphinx v9.1.0 corpus through `-b typstpdf` post-FID-01a: fatal-free (689-page `index.pdf`, valid `%PDF` magic), `unknown_visit` catalogue empty, and the SC#4 no-new-deps/no-`@preview`-bump invariant confirmed untouched — milestone v0.6.1's regression gate is closed.

---

## v0.6.0 real-world robustness (Shipped: 2026-07-13)

**Closeout:** override_closeout (milestone audit passed — 19/19 requirements, 16/16 integration seams wired, 5/5 E2E flows; pre-close artifact audit found 13 open debug sessions — non-fatal post-GATE-02 rendering-polish, acknowledged and deferred to the next milestone, see STATE.md Deferred Items)
**Phases:** 5 (11–15) · **Plans:** 15 · **Tasks:** 33
**Requirements:** 19/19 v1 requirements complete · **Known gaps:** none (13 non-fatal render-polish items deferred as next-milestone backlog)
**Git:** milestone work (173 commits) delivered via PR #115 (`release/v0.6.0 → main`, closes #114), merge commit `cc26b47`; tagged `v0.6.0` on the merge commit. A Windows-only CI false-negative (the corpus SC#2 `unknown_visit` parser was `^`-anchored and missed CRLF/leading-CR/location-prefixed warning lines) was root-cause-fixed on the PR before merge — the real gate (SC#1 fatal-free compile) passed on all platforms throughout.
**Released:** PyPI `typsphinx 0.6.0` (wheel + sdist) + GitHub Release `v0.6.0`, via `release.yml` (run 29210840198, green end-to-end)
**Code delta (milestone scope):** all work in `typsphinx/translator.py` (+ tests/fixtures); zero new runtime dependencies

**Delivered:** Sphinx's own full `doc/` tree now compiles end-to-end through the `typstpdf` builder with no fatal `TypstCompilationError` (Issue #114 closed) — fixing the two fatal figure/image bugs (px→pt length conversion + `:target:`/caption buffer-swap), adding correct rendering for the highest-frequency previously-dropped nodes (version directives, `refid` cross-references, autodoc `desc_*`, footnotes via a doctree pre-pass, transition/topic/line_block/glossary/tabular_col_spec/abbr), and a graceful-degrade net for out-of-scope graphical nodes — all behind a standing real-`typst.compile()` acceptance gate (GATE-01) and validated against the real corpus (GATE-02). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.

**Key accomplishments:**

- New `_convert_length_to_typst()` regex-based CSS-length-to-Typst converter wired into `visit_image` (fixes Issue #114's fatal `width: 200px` compile abort), plus a shared `_visit_graphical_placeholder()` helper giving `graphviz`/`inheritance_diagram` a visible bordered Typst `rect()` block + one warning + clean `SkipNode` instead of leaking source or aborting
- Figure captions now render through the normal visitor chain via buffer-swap (never `node.astext()`), consumed as a `{...}` code-block `caption:` argument, plus a new `refid` fallback branch in `visit_reference` so internal same-document `:target:` links compile alongside external-URL ones
- Extended `tests/test_pdf_render_gate.py` with three `slow`-marked real-compile test classes proving FIG-01/FIG-02/DEG-01/DEG-02 through `sphinx-build -> typst.compile() -> pypdf` — and, in the process, discovered and fixed a third, previously-hidden fatal Typst-compile bug (labels attached to code-mode statements are invalid Typst syntax) that this gate's own real-compile methodology was the only way to surface
- Unboxed italic version-directive labels (`versionadded`/`versionchanged`/`deprecated`/`versionremoved`) rendered by detecting Sphinx's own classed inline, with a real-compile GATE-01 fixture proving all four kinds plus the content-less case.
- Fixed the fatal dangling-`:term:`-anchor bug by emitting a bracket-wrap Typst `<label>` in `depart_term`, confirmed `visit_reference`'s refid branch was already correct, and proved both fixes with a real-compile `TestXrefRefidRenderGate` gate that would abort without them.
- Landed the four autodoc signature sub-part handlers -- `desc_returns` (return arrow), `desc_signature_line` (genuine `linebreak()`, resolving Open Question 1 empirically), `desc_optional` (recursion-safe nested brackets), and `desc_inline` (transparent pass-through, D-06) -- plus a real-compile GATE-01 fixture proving all four via `pypdf` text-extraction.
- Four small additive translator.py handlers -- transition-to-rule, glossary pass-through, tabularcolumns SkipNode, and stateless abbreviation-expansion -- proven correct through a real sphinx-build -> typst.compile() -> pypdf round-trip.
- Widened the load-bearing `visit_title`/`depart_title` buffer-swap to cover `nodes.topic` parents alongside `nodes.Admonition`, added `visit_topic`/`depart_topic` reusing the `clue` box helper, and fixed a pre-existing multi-child-title compile fatal — all four locked decisions (D-01/D-02/D-05/D-06) plus the Pitfall-1 fix landed as one atomic change per RESEARCH.md's atomicity mandate.
- Added visit_line_block/visit_line to translator.py so line-block content (addresses, epigraph shapes, poetry stanzas) renders with every line break preserved via a real `linebreak()`, and nested line blocks reproduce their structural indentation via a per-depth `h()` spacer — both compile-safe with zero markup-mode involvement.
- New `topic_line_block_render_gate` fixture + `TestTopicLineBlockRenderGate` class prove, via an uncaught real `typst.compile()`, that topic titles and `.. contents::` never leak into Typst's auto-outline (count==1), address/poem `line_block`s produce genuine `linebreak()`s (never source-`\n`-only concatenation), and the pre-existing multi-child admonition-title path (Pitfall 1) still renders correctly.
- Typst-native footnote rendering via a document-order pre-pass index in `visit_document`, with `visit_footnote_reference` emitting the compile-proven `[#footnote({body}) <fn-id>]` / `footnote(<fn-id>)` definition/reuse forms and `visit_footnote` suppressing the definition at its natural docutils location.
- A real `typst.compile()` acceptance fixture (`footnote_render_gate`) and `TestFootnoteRenderGate` class prove the Plan 14-01 footnote handlers compile cleanly end-to-end (SC#1-4), and in doing so caught and fixed a genuine paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap that would have made every realistic footnote citation a fatal compile abort.
- New `tests/test_corpus_gate.py` slow-marked pytest module that shallow-clones Sphinx's own `doc/` tree, wires in typsphinx, builds the full tree through `typstpdf`, and asserts the fatal-free PDF triple plus a frequency-ranked `unknown_visit` catalogue.
- Git-worktree-isolated depart_term XREF-01 revert + env-gated before/after empty-URL warning counter, both builds translate-phase-only (`-b typst`), added to `tests/test_corpus_gate.py`

---

A historical record of shipped versions. Full detail per milestone lives in `.planning/milestones/`.

---

## v0.5.0 — forward-ecosystem

**Shipped:** 2026-07-11
**Closeout:** verified_closeout (pre-close artifact audit clear; all 6 phases verified; milestone audit passed — 14/14 requirements, 5/5 integration seams, E2E release flow ready)
**Phases:** 6 (6–10 + 8.1) · **Plans:** 13 · **Tasks:** 29
**Requirements:** 14/14 v1 requirements complete · **Known gaps:** none
**Git:** milestone work on `release/v0.5.0`, merged to `main` via PR #112; tagged `v0.5.0` (on `main`)
**Released:** PyPI `typsphinx 0.5.0` (wheel + sdist) + GitHub Release, via `release.yml` (green end-to-end)
**Code delta (milestone scope, excl. `.planning/`):** 29 source/config files, +1025 / −467 lines

**Delivered:** Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1, docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the soft-deprecated docutils/Sphinx API surface, fixing a long-latent admonition markup/code-mode render bug (discovered once `docs-pdf` first compiled post-`kai`-fix), adding a `typst compile` smoke gate that guards all four packages, and releasing v0.5.0 to PyPI with the full 3-OS × Python 3.12–3.13 CI matrix observed green. Latest-only, no compatibility range.

**Key accomplishments:**

1. **Raised runtime pins + Python floor (Phase 6):** Re-pinned `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` and raised the Python floor to 3.12–3.13 across all 21 declaration sites (pyproject `requires-python`/classifiers, regenerated `uv.lock`, `tox.ini`, and the four GitHub Actions workflows) as one atomic pin-raise — both builders confirmed registering and a live `-b typst` build passing under Sphinx 9.1.
2. **Bumped `@preview` packages + typst 0.15 — the `kai` fix (Phase 7):** Raised `typst>=0.15.0,<0.16` and bumped mitex `0.2.4`→`0.2.7` (the actual fix, mitex PR #201), gentle-clues `1.2.0`→`1.3.1`, codly-languages `0.1.1`→`0.1.10` (codly `1.3.0` unchanged, registry ceiling), in lockstep across the 3-way version-sync — empirically closing the `unknown variable: kai` compile break via a real `tox -e docs-pdf` run producing a clean 101-page PDF.
3. **API & test compatibility (Phase 8):** Landed `traverse()`→`findall()` and modernized all soft-deprecated docutils/Sphinx call sites (`OptionParser`→`get_default_settings`, `builder.app`→`_app`, `writer_name`→`writer=get_writer_class(...)()`), then installed a permanent pytest `filterwarnings` guard escalating both `DeprecationWarning` and `PendingDeprecationWarning` — full suite green, zero `traverse()` remaining.
4. **Admonition rendering fix (Phase 8.1, inserted):** Rewrote `_visit_admonition`/`_depart_admonition` to emit gentle-clues code-mode content-blocks (`info({...})`) instead of markup-mode brackets (`info[...]`), preserved inline-markup titles via a buffer-swap (also fixing a latent title double-emission bug), added the five previously-unimplemented types (`hint`/`error`/`danger`/`attention`/generic `.. admonition::`), and proved it with a real `sphinx-build → typst.compile() → pypdf` PDF-text-extraction acceptance gate.
5. **Green CI matrix + smoke gate + guardrails (Phase 9):** Observed all 13 CI jobs green for the first time on Sphinx 9.1/docutils 0.22/typst 0.15 across all 3 OS runners (PR #112); added a `typst compile` smoke gate (`tests/test_preview_smoke_gate.py`) exercising all four `@preview` packages via real calls — closing the coverage gap the historical `kai` regression slipped through, proven with a negative control; reconciled stale `main` branch-protection required-checks; confirmed the dependency-ceiling guardrails (`sphinx<10`/`typst<0.16`/`docutils<0.23`).
6. **Version single-source + v0.5.0 release (Phase 10 + milestone close):** `typsphinx.__version__` now derives from `importlib.metadata` (retiring the stale `0.4.3`) with `pyproject.toml` the sole `0.5.0` literal, `uv.lock` regenerated, plus an independent `tomllib` drift-guard test; curated `CHANGELOG.md` `## [0.5.0]` entry as the Release-body source; publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI + GitHub Release) executed at milestone close, mirroring the v0.4.4 precedent.

**Deferred:** CFG-01 (was FWD-03 — user-configurable `@preview` versions) and XOS-01 (cross-OS docs-PDF CI on macOS/Windows) → v2. Phase 8's multi-`<term>` definition-list hardening deferred as forward-looking (no current docutils 0.22.4 rST syntax emits a multi-`<term>` node).

**Archives:** `milestones/v0.5.0-ROADMAP.md`, `milestones/v0.5.0-REQUIREMENTS.md`, `milestones/v0.5.0-MILESTONE-AUDIT.md`

---

## v0.4.4 — CI-repair + modernize

**Shipped:** 2026-07-05
**Closeout:** verified_closeout (pre-close artifact audit clear; all 5 phases verified)
**Phases:** 5 (1–5) · **Plans:** 15 · **Tasks:** ~35
**Requirements:** 23/23 v1 requirements complete · **Known gaps:** none
**Git:** milestone work merged to `main` via PRs #104 / #105 / #106; close + release-prep via #109; tagged `v0.4.4` (on `main` dae500a)
**Released:** PyPI `typsphinx 0.4.4` (wheel + sdist) + GitHub Release, via release run 28731646924 (green end-to-end)
**Code delta (milestone scope):** ~15 source/config files, +217 / −1202 lines (net, incl. `uv.lock` collapse)

> **Release note:** The first `v0.4.4` tag push failed at the `release.yml` Validate gate — the
> version-verify step imported stdlib-only `tomllib` on the 3.10 floor (a PYVER-02 side effect
> only exercised at tag time). Fixed with a `tomllib`/`tomli` fallback (PR #110), tag re-pointed,
> release re-run green. This also resolved D-11 (`softprops/action-gh-release@v3` ran green).

**Delivered:** Restored a fully green CI pipeline on `main` — lint, the 3-OS × Python 3.10–3.13 test matrix (19 jobs), coverage, and the docs PDF build — by pinning the runtime dependency graph back to a known-good, reproducible combination, then modernized the Python floor and dev tooling and installed durability guardrails so the drift can't silently recur.

**Key accomplishments:**

1. **Root-cause pin (Phase 1):** Pinned `typst>=0.14.1,<0.15` (with precautionary `sphinx<9` / `docutils<0.22` ceilings), regenerated `uv.lock`, mirrored tox ceilings, and removed the dead `sphinx-testing` dep — fixing the `typst.TypstError: unknown variable: kai` break from a bundled `@preview` package under typst 0.15.
2. **Verified green baseline (Phase 2):** Confirmed every previously-red CI job green across the full matrix (incl. the 7 PDF-integration tests and `docs.yml` multi-language PDF-copy), and guarded the 3-way `@preview` version sync with an automated desync test.
3. **Modernized Python floor (Phase 3):** Bumped the supported range to 3.10–3.13 across every config surface (pyproject, tox, CI/docs/release workflows, black/ruff/mypy target-versions) as one atomic, CI-verified batch.
4. **Refreshed dev tooling (Phase 4):** Conservative floor+ceiling bumps for pytest/mypy/black/ruff/tox; artifact actions to node24 ahead of GitHub's 2026-09-16 Node-20 removal; removed the stale `Test Python 3.9` required check.
5. **Durability guardrails (Phase 5):** `uv sync --locked` at all 9 sites (DUR-01), a standalone weekly + dispatch `drift.yml` forward-drift detector with deduplicated issue reporting (DUR-02), a scoped `sphinx-typst-stack` Dependabot group (DUR-03), and a README CI status badge (DUR-04).

**Deferred:** D-11 (`softprops/action-gh-release@v3` tag-gated runtime confirmation) — signed off to the next real release tag (this v0.4.4 release exercises it). v2 forward-ecosystem support (FWD-01/02/03: Sphinx 9, typst 0.15+, configurable `@preview` versions) remains out of scope.

**Archives:** `milestones/v0.4.4-ROADMAP.md`, `milestones/v0.4.4-REQUIREMENTS.md`

---
