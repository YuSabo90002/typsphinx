# Phase 41: v0.7.0 Release Automation + Release Prep - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Prep-only release work for v0.7.0, plus the one piece of release *automation* the milestone scoped.
**Requirements: REL-04 (whole) and REL-05 (the prep half only — the publish half executes at
`/gsd-complete-milestone`).**

**In scope:**

- **REL-04 — `.github/workflows/release.yml`'s release-notes body.** Measured 2026-08-02: the
  `create-release` job's `Generate release notes` step (`release.yml:152-174`) builds the body from
  `git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` (line 164) plus an Installation block
  (lines 170-174); `release.yml` never opens `CHANGELOG.md` anywhere. `main..HEAD` is **328
  commits**, so the dump would be a 328-line body (v0.6.4's was 296 lines of dump inside a 308-line
  body). Replace the dump with a `## [X.Y.Z]` extraction from `CHANGELOG.md` per D-06..D-09.
- **REL-05 prep half.** `pyproject.toml:7` — `version = "0.6.5"` → `"0.7.0"` (measured: still the
  sole version literal; `typsphinx.__version__` derives from `importlib.metadata`), `uv.lock` in
  lockstep (acceptance: `uv sync --extra dev --locked` green), and `README.md:317`
  (`**Status**: Stable (v0.6.5) - Production ready` → `v0.7.0`; `tests/test_readme_version_sync.py`
  asserts the two agree).
- A curated `## [0.7.0]` entry in `CHANGELOG.md` per D-01..D-05, **plus the tail link-block
  rollover** — add the `[0.7.0]` release-tag line and advance `[Unreleased]` to `v0.7.0...HEAD`
  (ROADMAP SC#2; this is release-prep's own job, not `/gsd-complete-milestone`'s).
- **SC#3 live-run evidence on the post-bump tree:** full pytest, the lint/type trio
  (`black --check .` / `ruff check .` / `mypy typsphinx/`), the full-corpus (Sphinx v9.1.0 `doc/`)
  `-b typstpdf` gate, both docs dogfooding builds (`tox -e docs-html`, `tox -e docs-pdf`), **and**
  the `ja` build's four-check glyph bar per D-15..D-17.
- **SC#4 milestone-invariant proof over the SHA-anchored full milestone diff** — zero new runtime
  dependencies, the `@preview` package count still four with no new version-lockstep site, and every
  node-handler change carrying its recorded-RED GATE-01 fixture. Per D-11 this verification range
  **includes Phase 40.1's handler changes**, not only Phases 36-40's.
- The `visit_desc_sig_name` docstring fix (D-12) — the one `typsphinx/` change this phase takes.
- Planning-record hygiene (D-13): file the two already-resolved todos to `todos/completed/` and
  terminate PROJECT.md's two unterminated HTML comments.
- **SC#5 handoff:** a standalone `41-HANDOFF.md` checklist recording exactly what
  `/gsd-complete-milestone` will execute (merge → tag → `release.yml` → PyPI + GitHub Release →
  the standing second tag on `typsphinx-doc-translations`), following the `35-HANDOFF.md` precedent.

**Out of scope:**

- **Any publish or otherwise irreversible action** — `git tag v0.7.0`, triggering `release.yml`,
  PyPI, the GitHub Release, opening or merging the PR. SC#5 requires local *and* remote `v0.7.0`
  tags to both be empty at phase close. The prep/publish fence is absolute (Phase 33/35 precedent).
- **Phase 40's review warnings WR-01 / WR-02 / WR-03** — routed to a newly inserted **Phase 40.1**
  (D-11). Phase 41 does not fix them and does not file them as todos.
- Four pending todos deferred to v0.7.1+ (D-14): the `sphinx-build -b linkcheck` CI job, the
  non-`str` docname `TypeError` in `TypstPDFBuilder.finish()`, `derive_typst_lang()`'s duplicated
  warning block, and the typing modernization (the last is explicitly deferred by `CLAUDE.md`).
- Any `typsphinx/` change other than D-12's docstring escape.
- Changes under `docs/` — measured: `docs/` did not change by a single line this milestone, and
  touching it drags in gettext-catalog follow-up in the translations repository (Phase 28 D-04 /
  Phase 33 / Phase 35 rule).
- Flipping the REL-04 / REL-05 checkboxes and traceability rows in `.planning/REQUIREMENTS.md` —
  close side, at `/gsd-complete-milestone`. **Watch for the known `phase.complete` hazard that
  auto-flips a deferred requirement's checkbox against the CONTEXT decision; check the diff before
  committing and revert if it fires.**
- Revisiting the version number itself (0.7.0 is fixed by ROADMAP SC#2).
- Editing historical CHANGELOG entries.

</domain>

<decisions>
## Implementation Decisions

Every measured value below was taken **this session (2026-08-02)** against the live tree, not from
recall: `main..HEAD` commit count, the `release.yml` line numbers and job dependency order, the
version-literal sites, the pending-todo states (including two that are already fixed in code), and
the milestone diff's font handling.

### CHANGELOG `## [0.7.0]` entry

- **D-01: Bullets are cut at user-visible-change granularity — 5 to 6 of them — with requirement IDs in trailing parentheses.** Direct continuation of Phase 33 D-09's granularity rule, already carried forward. The expected shape: signatures becoming real typography (SIG-01..09); description bodies and field lists indenting by nesting depth (IND-01..05, FLD-01..03); the admonition bucket re-taxonomy and rubric indentation (ADM-01..06); citations as a full round trip (CIT-01..06); the redundant blank line after block math in a list item (MATH-02). Rejected: one bullet per requirement ID (32 bullets — full traceability, but splitting "what part of the signature line became what" across five bullets does not read as release notes), and a three-bullet family-level roll-up (buries single large changes like IND-02, the one that makes class membership visually recoverable).

- **D-02: Section split is `### Added` for CIT, `### Changed` for SIG/IND/FLD/ADM, `### Fixed` for MATH-02.** Keep a Changelog semantics taken literally: citation handlers were greenfield (zero handlers existed; a citation aborted the compile outright), so CIT is Added; MATH-02 is a defect carried over from v0.6.5's Phase 34 review, so it is Fixed. Rejected: collapsing everything under `### Changed` as one "re-drawing" narrative — CIT-01 (a document containing a citation could not compile at all) is not a "change".

- **D-03: No BREAKING label. The rendering change is stated explicitly in the lead paragraph instead.** Extends 0.6.5 D-01's axis ("no BREAKING when no user's working setup breaks"): measured, not one `typst_*` config value, builder name, or template parameter changed this milestone — what changed is the appearance of the emitted `.typ` and compiled PDF. Rejected: a BREAKING-labelled bullet inside `### Changed`, and a new `Upgrade notes` subheading (would add a heading shape the CHANGELOG has never carried).

- **D-04: The lead paragraph's axis is "API reference pages became readable."** It follows the milestone name (API rendering design overhaul) and ROADMAP's goal sentence — from a flat wall of proportional bold text to a reference document. Citations are secondary in the lead. Rejected: leading with the core-value phrasing ("correct → well typeset"), and leading with the change-surface facts (accurate but defers what actually got better).

- **D-05: `### Verified` carries exactly the same three items as 0.6.5.** Zero new runtime dependencies across the full milestone diff; the four bundled `@preview` package version strings unchanged across every sync surface; the full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free. Rejected: adding the two docs dogfooding builds and adding ADM-04's owner visual sign-off — both are run and recorded as SC#3/SC#4 evidence, but 0.6.5's rule that test/verification machinery is not user-visible holds.

### REL-04 — `release.yml` release-notes body

- **D-06: The `## [X.Y.Z]` extraction lives in a committed script that `release.yml` calls, with a pytest around it.** Puts release-surface correctness on the same footing as `tests/test_readme_version_sync.py` and `tests/test_preview_version_sync.py` — the extraction is exercised on every CI run, not only when a tag is pushed. `scripts/` is an established location in this repository (`scripts/render_admonition_greyscale.py` landed this milestone). Rejected: an inline `awk`/`sed` block in the workflow (self-contained but unreachable from pytest, so a break is discovered at tag time), and inline shell plus a separately-implemented pytest (two implementations, so a divergence in the extraction itself is invisible).

- **D-07: SC#1's "executed against the real file for a real version" is discharged by a hand-run transcribed verbatim into the phase's GATE-EVIDENCE file.** The project's standard evidence shape — the command, its input, and its output pasted as run. Rejected: downloading the real v0.6.5 GitHub Release body for a side-by-side line count (would answer REL-04's motivation directly but needs network access and is not what SC#1 asks for).

- **D-08: `generate_release_notes` stays enabled at `true`, and the Installation block stays.** Follows the todo's recorded design direction, and 35-CONTEXT D-11's measurement: GitHub's auto-generated portion of the v0.6.4 body was 5 lines (one "What's Changed" PR line plus the Full Changelog compare link) — already compact. The bloat was entirely the hand-rolled `git log` block. Note the structural consequence: `body_path` and `generate_release_notes: true` are used together on `softprops/action-gh-release`, so the auto notes are *appended* to the curated body rather than replacing it.

- **D-09: The fail-loud check moves forward into the `validate` job.** Measured job order: `validate` → `build` → `publish-pypi` → `create-release`. A missing `## [X.Y.Z]` section detected only in `create-release` would fail *after* the PyPI upload, leaving "published to PyPI but no GitHub Release." Put the existence-and-non-emptiness check next to the existing tag-vs-`pyproject.toml` version check (`release.yml:50-59`), which already establishes the "verify before publishing" position in that job.

- **D-10 [derived, not separately asked]: the pytest covers both directions.** A real version present in `CHANGELOG.md` extracts a non-empty section, and an absent version (e.g. `9.9.9`) exits non-zero — the failure mode the todo names ("publish a release with an empty or malformed body"). This follows directly from D-06 + D-09; the planner may adjust the exact case list but must not leave the failure path untested.

### Scope — what this phase closes and what it routes elsewhere

- **D-11: Phase 40's WR-01 / WR-02 / WR-03 are closed in a newly inserted Phase 40.1, not in Phase 41.** Owner's ruling after being shown the sizing: WR-01 is a one-line fix (`ref_node is None or not …`), WR-02 adds three lines to a skip condition, WR-03 is a genuine design change (the D-14 eligibility predicate is duplicated across `visit_reference` and `_citing_reference_has_own_anchor` with an unenforced invariant between them). The deciding factor was not size but the RED question: `40-REVIEW.md` states all three sit on paths the fixture does not exercise and that **none was reproduced against a real Sphinx build**, while milestone invariant #4 requires every node-handler change to carry a recorded-RED GATE-01 fixture — and proving exactly that mechanically is Phase 41's own SC#4. Closing them inside Phase 41 would mean Phase 41 enlarging its own proof obligation, on the translator, immediately before a release. Precedent for the insertion: Phases 8.1, 30.1, and Phase 39's gap-closure plans. **Two consequences for planning: (a) Phase 41's SC#4 invariant sweep must cover Phase 40.1's handler changes as well as Phases 36-40's; (b) inserting Phase 40.1 into `ROADMAP.md` is a separate `/gsd-phase` action and is NOT Phase 41 work.**

- **D-12: The `visit_desc_sig_name` docstring fix is taken in Phase 41.** `typsphinx/translator.py:6415` still carries the phrase `PyTypeObject *type`; the unbalanced `*` makes autodoc emit `WARNING: Inline emphasis start-string without end-string` and a stray `problematic` node into the published API reference. It is a docstring escape — the emitted `.typ` shape does not change, so it creates no GATE-01 fixture obligation — and SC#3 runs `tox -e docs-pdf` anyway, so the warning disappears from evidence this phase already collects. Rejected: bundling it into Phase 40.1 (unrelated to that phase's citation subject).

- **D-13: Both planning-record hygiene items are done in Phase 41.** File the two todos that are already fixed in code to `todos/completed/` — measured: `_desc_break_marker` is now a `(id(self.body), len(self.body))` tuple (`typsphinx/translator.py:189`, compared at `:5352` and `:5695`), and `EXPECTED_PAGE_COUNT_PRE_PHASE` was renamed to `EXPECTED_PAGE_COUNT_CEILING` (`tests/test_signature_page_boundary_render_gate.py:147`) — and terminate PROJECT.md's two unterminated `<!-- Prior: …` comments (lines 492 and 506 as measured at commit `279aea5`). Neither touches code.

- **D-14: The remaining four pending todos are deferred to v0.7.1+.** The `sphinx-build -b linkcheck` CI job, the non-`str` docname `TypeError` in `TypstPDFBuilder.finish()`, `derive_typst_lang()`'s duplicated warning block, and the typing modernization. None relates to REL-04/REL-05 and none blocks the release; the typing one is explicitly deferred by `CLAUDE.md`. The linkcheck job specifically was weighed and declined: v0.6.4 already added the advisory repository-wide `links.yml` (lychee), which covers the one new link this release adds to `CHANGELOG.md`'s tail block.

### SC#3 — the `ja` four-check glyph bar

Why this is a success criterion at all: Typst's font fallback is silent — no warning, no error — so a
PDF with substituted glyphs builds clean, downloads clean, and extracts the correct characters. The
four checks (Phase 29 D-12 / Phase 30.1 D-03) are: (1) page count, (2) extracted text, (3) embedded
`/BaseFont` CJK-coverage enumeration, (4) owner visual confirmation.

**Measured mitigating fact, and the residual exposure:** this milestone never names a font family —
`typsphinx/translator.py`'s own docstring records "Monospace is reached ONLY through Typst's
`raw(...)` primitive -- never by naming a font family, which would silently shadow the Japanese
build's CJK fallback with neither a warning nor an error", and `typsphinx/templates/base.typ` still
sets only `size` and `lang`, no family. But the milestone added **24 new `raw(` call sites**, and
`raw()` resolves to Typst's default monospace family, which has no CJK coverage. The exposure is
real even though no family name was written.

- **D-15: The comparison is main-vs-HEAD, both built locally.** Build the `ja` documentation twice on the same machine with the same toolchain and font environment — once from `main`, once from `HEAD` — and run the four-check bar across the pair. This isolates the difference to v0.7.0's own changes. Rejected: downloading RTD's currently-served `ja` PDF as the "before" (real published artifact, but RTD builds on an `ubuntu-24.04` image with `fonts-noto-cjk` provisioned, so environment differences become noise), and reusing Phase 30.1's recorded values (94 pages / 1,811,337 bytes / 9 embedded fonts / 1,997 CJK characters in the first 30 pages — one build cheaper, but those are v0.6.4-era values with v0.6.5's translator changes in between, so a diff could not be attributed to v0.7.0).

- **D-16: Check 4 — the owner's visual confirmation — is a Phase 41 close condition, collected inside the phase.** Same shape as ADM-04's sign-off in Phase 39 (`39-ADM04-SIGNOFF.md`). The pages to inspect are chosen by measured CJK density, following Phase 30.1's method rather than by taste. Rejected: recording it as `human_needed` and carrying it into the handoff (30.1's form), and skipping the visual look when the check-3 `/BaseFont` sets match byte-for-byte between the two builds.

- **D-17: The `typsphinx-doc-translations` clone lives inside the phase directory.** `.planning/phases/41-v0-7-0-release-automation-release-prep/translations-repo/`, following Phase 30.1's precedent — where it was likewise a working clone that was never committed (it is absent from the archived phase directory). Record the cloned SHA verbatim in the evidence file so the comparison is reproducible.

### Claude's Discretion

The following are for the researcher / planner / executor to decide:

- The exact wording of the `[0.7.0]` entry, the lead paragraph's phrasing, how requirement IDs are
  attached, and which 5 or 6 bullets the D-01 list resolves to.
- The extraction script's language, filename, CLI shape, and how `release.yml` invokes it in both
  the `validate` and `create-release` jobs (D-06 fixes only that it is committed and pytest-covered;
  D-09 fixes only that the existence check runs in `validate`).
- The pytest module's name and its exact case list beyond D-10's two directions. Note the measured
  quirk the extractor must not trip on: `CHANGELOG.md` currently contains **two** `## [Unreleased]`
  headings (the Keep-a-Changelog one near the top and a "Planned for Future Releases" one in the
  tail block).
- Plan decomposition and ordering within the phase, and the `uv.lock` regeneration procedure
  (acceptance: `uv sync --extra dev --locked` green).
- The mechanical method for SC#4's "every node-handler change carries its recorded-RED GATE-01
  fixture" over the +1,699-line `typsphinx/translator.py` diff (the owner declined to pre-decide
  this; a changed-`visit_`/`depart_`-handler census mapped against gate modules is the obvious
  shape).
- The format and heading structure of `41-HANDOFF.md`.
- Where live-run evidence is recorded. **`41-VERIFICATION.md` is a name reserved by the verifier and
  will be clobbered** — a plan that accumulates evidence must use a different name (e.g.
  `41-RELEASE-EVIDENCE.md`, the Phase 35 precedent) or plan a backup-and-remerge.

### Folded Todos

- **`.planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md`** — "The
  GitHub Release body should be the CHANGELOG section, not a commit dump" (`resolves_phase: 41`).
  This todo *is* REL-04; its recorded design direction is adopted with two refinements: the
  extraction is a committed, pytest-covered script (D-06) rather than unspecified, and the fail-loud
  check moves into the `validate` job (D-09) rather than living only in `create-release`.

- **`.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`**
  — folded per D-12.

- **`.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md`** — folded per
  D-13.

- **`.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md`** and
  **`.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`**
  — folded per D-13 as *record* work only: both are already fixed in code (verified this session);
  Phase 41 files them to `todos/completed/`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's requirements and success criteria

- `.planning/ROADMAP.md` § "Phase 41: v0.7.0 Release Automation + Release Prep" — the five success
  criteria this phase is judged against.
- `.planning/REQUIREMENTS.md` § "Release and CI (REL)" — REL-04 and REL-05 verbatim, plus the
  traceability rows that stay `Pending` until `/gsd-complete-milestone`.
- `.planning/REQUIREMENTS.md` § "v1 Requirements" (SIG / IND / FLD / ADM / CIT / MATH) — the source
  for the CHANGELOG bullets' requirement IDs and for what each family actually delivered.

### The release-prep precedent to follow

- `.planning/milestones/v0.6.5-phases/35-v0-6-5-release-prep/35-CONTEXT.md` — the prep/publish
  fence, the version-literal census, D-11's measurement of the v0.6.4 release body, and D-12's
  live-run evidence scope.
- `.planning/milestones/v0.6.5-phases/35-v0-6-5-release-prep/35-HANDOFF.md` — the handoff document
  shape SC#5 asks for.
- `.planning/milestones/v0.6.5-phases/35-v0-6-5-release-prep/35-RELEASE-EVIDENCE.md` — the
  evidence-file shape, and the reason it is not named `35-VERIFICATION.md`.

### REL-04's own source material

- `.planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md` — the measured
  problem statement, the design direction, and the named failure mode.
- `.github/workflows/release.yml` — `validate` job's version check at lines 50-59; `create-release`
  job's `Generate release notes` step at lines 152-174 and `Create GitHub Release` at lines 176-187.
- `CHANGELOG.md` — the `## [0.6.5]` entry as the structural model, and the tail link block.

### The `ja` glyph bar

- `.planning/milestones/v0.6.4-phases/30.1-translations-repository-japanese-rtd-site/30.1-06-PLAN.md`
  — the four-check bar executed end to end, including the exact `pypdf` invocation shape and the
  honest `human_needed` recording of check 4.
- `.planning/milestones/v0.6.4-phases/30.1-translations-repository-japanese-rtd-site/30.1-CONTEXT.md`
  § D-03 — the bar's definition and the measured local ja baseline.
- `.planning/milestones/v0.6.4-phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md`
  § "D-12 Baseline (local, this commit)" — the comparison method to replicate.
- `.planning/milestones/v0.6.4-phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-RESEARCH.md`
  § D-14 — why text extraction alone cannot detect glyph substitution.

### Phase 40.1's source (routed away from this phase, but SC#4 must cover its output)

- `.planning/phases/40-citations-full-round-trip/40-REVIEW.md` § Warnings — WR-01, WR-02, WR-03 with
  their file/line locations and proposed fixes.
- `.planning/phases/40-citations-full-round-trip/40-CONTEXT.md` — D-01..D-10, the design the
  warnings sit inside.

### Standing project constraints

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree `uv sync` +
  `uv run` provisioning for every executor.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — the sync surfaces SC#4's invariant sweep
  counts.
- `.planning/STATE.md` § "Active Milestone (v0.7.0)" — the milestone invariants, the GATE-01
  redefinition (invariant #4), and the standing `--skip-ui` / api-coverage false-positive notes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tests/test_readme_version_sync.py` and `tests/test_preview_version_sync.py` — the established
  "a release-surface fact is pinned by pytest" pattern D-06's new test joins. `test_readme_version_sync`
  also means the `pyproject.toml` and `README.md` bumps must land together or the suite turns red.
- `scripts/render_admonition_greyscale.py` — precedent that `scripts/` holds committed helper
  scripts in this repository (added this milestone).
- `.github/workflows/release.yml:50-59` — the existing "verify before publishing" check in the
  `validate` job; D-09's new check goes beside it.
- `.github/workflows/links.yml` — the advisory repository-wide lychee link check already covering
  the new `CHANGELOG.md` tail link (part of why D-14 declines the linkcheck todo).

### Established Patterns

- **Version literals:** `pyproject.toml:7` is the sole literal; `typsphinx.__version__` derives from
  `importlib.metadata`; `README.md:317` carries the human-readable status line; `uv.lock` must move
  in lockstep.
- **CHANGELOG entry shape:** lead paragraph → `### Added` / `### Changed` / `### Fixed` →
  `### Verified` → tail link block. `[0.6.5]`, `[0.6.4]`, `[0.6.3]`, and `[0.6.1]` all follow it.
- **Evidence culture:** commands and their output transcribed verbatim; `human_needed` recorded
  honestly rather than asserted; the honest-verifier rule (abstain rather than assert without direct
  evidence).

### Integration Points

- `release.yml` ↔ `CHANGELOG.md` — the link REL-04 creates. It does not exist today: measured, the
  workflow never opens `CHANGELOG.md`. Phase 33's CONTEXT claim that the `[0.6.4]` entry was "the
  single source for the GitHub Release body" only becomes true when this phase lands.
- The post-bump tree ↔ the `typsphinx-doc-translations` repository — no `.gitmodules` and no
  submodule are present in this checkout (measured this session), and `docs/` has no `locale/`
  directory, so the `ja` build of D-15 requires the external clone of D-17.
- Phase 41's SC#4 sweep ↔ Phase 40.1's translator changes — a cross-phase dependency introduced by
  D-11. Phase 41 cannot run its final invariant sweep until Phase 40.1 has landed.

</code_context>

<specifics>
## Specific Ideas

- The owner explicitly asked whether WR-01/02/03 warranted their own phase rather than accepting
  either the "close it here" or "defer to a todo" framing — the inserted Phase 40.1 is the owner's
  own construction, not a menu option.
- On the CHANGELOG, the owner chose the reading experience over traceability at every fork: bullets
  at the user-visible-change level, a lead paragraph organised around "API reference pages became
  readable", and a `### Verified` section held to the same three items as 0.6.5 rather than grown.
- On `release.yml`, the owner chose the more-infrastructure option (committed script + pytest) but
  the lighter proof option (hand-run transcript rather than a diff against the live v0.6.5 release
  body) — the durable part gets machinery, the one-off proof does not.
- On the `ja` glyph bar, the owner chose the most expensive but causally cleanest option (two local
  builds) and refused to let a matching `/BaseFont` set substitute for the visual look.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 40.1 (to be inserted) — WR-01 / WR-02 / WR-03.** Not a "someday" item: the owner's
  decision is that these ship inside v0.7.0, in their own phase, before Phase 41's final invariant
  sweep. Inserting the phase into `ROADMAP.md` is a `/gsd-phase` action outside Phase 41's scope.
  The open design question that phase must settle is how to take a RED for defects that
  `40-REVIEW.md` records as unreproduced against a real Sphinx build — a `sphinx-build` fixture that
  constructs the missing citing-site topology, or a doctree assembled directly against the
  translator in the `tests/test_translator.py` style.

### Reviewed Todos (not folded)

- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — deferred to v0.7.1+ per D-14; `links.yml`
  already covers the one new link this release adds.
- **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** — deferred to v0.7.1+ per D-14;
  a builder-side behaviour change, unrelated to REL-04/REL-05.
- **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** — deferred to v0.7.1+ per D-14; a
  refactor with no release bearing.
- **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** — deferred to v0.7.1+ per
  D-14, and independently held back by `CLAUDE.md`'s standing instruction.

</deferred>

---

*Phase: 41-v0-7-0-release-automation-release-prep*
*Context gathered: 2026-08-02*
