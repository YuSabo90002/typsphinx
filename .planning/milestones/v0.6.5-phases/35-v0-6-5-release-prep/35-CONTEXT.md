# Phase 35: v0.6.5 Release Prep - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Prep-only release preparation for v0.6.5. **Requirements: REL-03 (the prep half only — the publish
half executes at `/gsd-complete-milestone`).**

**In scope:**

- `pyproject.toml:7` — `version = "0.6.4"` → `"0.6.5"` (measured: this is the sole version literal;
  `typsphinx/__init__.py` derives from `importlib.metadata` and is not a bump target) plus
  `uv.lock:1379` in lockstep (acceptance: `uv sync --extra dev --locked` green)
- `README.md:317` — `**Status**: Stable (v0.6.4) - Production ready` → `v0.6.5`
  (`tests/test_readme_version_sync.py` asserts the two agree — changing only one turns the suite red)
- A curated `## [0.6.5]` entry in `CHANGELOG.md` (structure per D-01–D-04) plus the tail link-block
  rollover: add the `[0.6.5]` release-tag line and advance `[Unreleased]` to `v0.6.5...HEAD`
  (ROADMAP SC#2 states this is release-prep's own job)
- **Closing the three test-side Warnings from the Phase 34 review (WR-02 / WR-03 / WR-04)**
  (D-05–D-07). Not one line under `typsphinx/` is touched — fixture and gate-test additions only,
  so milestone invariant #3 is not violated
- Asserting the milestone invariants mechanically over the full diff (ROADMAP SC#4): take
  `git diff` over merge-base `eb696bb`..HEAD (measured: 33 commits) and record, with evidence, zero
  new runtime dependencies / no `@preview` bump / the four sync-surface version strings unchanged
- Live-run evidence (ROADMAP SC#3 + D-12): full pytest, `black` / `ruff` / `mypy`, the full-corpus
  `-b typstpdf` gate, **plus the two docs dogfooding builds** (`tox -e docs-html`, `tox -e docs-pdf`)
- A handoff document `35-HANDOFF.md` for `/gsd-complete-milestone` (D-09)
- Filing todos for the findings deliberately not picked up (D-10, D-11): WR-01, and the
  release-notes-body rework in `release.yml`

**Out of scope:**

- **Any publish action** (`git tag v0.6.5`, triggering `release.yml`, PyPI, GitHub Release, opening
  or merging the PR) → `/gsd-complete-milestone`. The ROADMAP's prep/publish fence is absolute
- Changes under `typsphinx/` (milestone invariant #3). WR-01's fix requires a translator change and
  therefore lands here (D-05)
- Changes to `.github/workflows/release.yml` (D-11 — filed as a todo for v0.6.6+)
- Changes under `docs/` (touching them drags in gettext catalog follow-up in the translations
  repository — same rule as Phase 28 D-04 and Phase 33)
- Flipping the REL-03 checkbox / traceability row in `.planning/REQUIREMENTS.md` (D-10 — close side)
- The five pending todos and the v2 requirements (already decided in
  `.planning/REQUIREMENTS.md` § Out of Scope)
- The three 30.1-review Warnings (same § Out of Scope)
- Revisiting the version number itself (0.6.5 is fixed by ROADMAP SC#1)
- Editing historical CHANGELOG entries

</domain>

<decisions>
## Implementation Decisions

### Structure of the `## [0.6.5]` CHANGELOG entry

- **D-01: The `### Fixed` body uses one general sentence with representative contexts in parentheses.**
  Measured: the shape the backlog report (999.1) named — inline math immediately after text in a
  top-level paragraph, including the no-intervening-space form — was already green before the fix.
  What was actually red: bullet-list items, field bodies (`confval`'s `:type:` / `:default:`),
  definition-list terms, display math inside a list item, and a list item whose sole content is
  inline math. Write it as "inline math immediately after text (in bullet-list items, definition-list
  terms, and the like)" on one line; do not enumerate every context. **No BREAKING label** — this is
  a pure bug fix with no user whose working setup breaks.

- **D-02: Display math inside a list item goes in the same bullet as inline math.**
  The construct in question is a `.. math::` block inside a list item.
  From the user's side this is one and the same change — "math inside a list item made the build
  fail" — so it is bundled (precedent: Phase 33 D-09's granularity rule — bundle by user-visible
  change, requirement IDs in trailing parentheses). The implementation-level split between
  `visit_math` and `visit_math_block` does not surface in the CHANGELOG.

- **D-03: Two sections — a lead paragraph plus `### Fixed` and `### Verified`.** This matches
  0.6.1 / 0.6.3 / 0.6.4, all of which carry a lead paragraph and a Verified section. The lead's axis:
  the separator-omission compile abort for inline and display math is fixed, and the only runtime
  change is one site in the translator.

- **D-04: `### Verified` carries three items — the two invariants plus the full-corpus gate.**
  Zero new runtime dependencies / the four `@preview` version strings unchanged / the full-corpus
  (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run is fatal-free. Because this milestone does touch the
  translator, the Phase 23/28 corpus item is justified here (Phase 33 D-03 omitted it precisely
  because that milestone had zero `typsphinx/` changes). The GATE-01 fixture's RED→GREEN record is
  **not** listed — test machinery is not user-visible.

### Handling the four Warnings from the Phase 34 review

- **D-05: Close only the three test-side Warnings (WR-02 / WR-03 / WR-04) in Phase 35; file WR-01 as a todo.**
  WR-02–04 are fixture and gate-test additions with zero `typsphinx/` change, so invariant #3 is
  untouched. WR-01 (`visit_math_block`'s pre-existing unconditional `"\n\n"` doubling up with the new
  `list_item_needs_separator` flag, emitting one redundant blank line) is inert in Typst but requires
  a translator change, which would force re-deriving the GATE-01 fixture's expected strings and
  re-running the full-corpus gate. We are not taking on an output-shape change immediately before a
  release.

- **D-06: Close WR-02 by adding Construct G to the existing fixture.** Add "a `:label:`-bearing
  `.. math::` inside a list item" to
  `tests/fixtures/inline_math_after_text_render_gate/index.rst` and add assertions to both the mitex
  and native tests. A separate fixture would add two more `sphinx-build` runs, so keep it consolidated
  with the existing six constructs (A–F).

- **D-07: The three test additions run as an independent plan before the version bump.**
  The ROADMAP gains no new success criterion.
  Phase 35's SC#1–SC#4 say nothing about test additions, so this is
  recorded here as work adjacent to (outside) REL-03's scope: get it green first, then the version
  bump / CHANGELOG / SC#3 live-run evidence establish the final green in a single pass. We do not add
  an SC#5 to the ROADMAP and thereby widen the phase boundary officially.

### Handoff to `/gsd-complete-milestone`

- **D-08: The two-repository tagging standing cost (v0.6.4 D-07) holds for v0.6.5 as well.** Measured:
  the translations repository `typsphinx-doc-translations` carries only the tag `v0.6.4`, and RTD's
  en `stable` is likewise tag `v0.6.4` (identifier `2bf6ef3`). `docs/` did not change by a single line
  this milestone, so the translated content is identical — but without the tag, the version shown on
  `/ja/stable/` would diverge from `/en/stable/`. No exception: bump the submodule and tag `v0.6.5`.

- **D-09: Write a dedicated `35-HANDOFF.md`.** Following the `33-HANDOFF.md` precedent. Phase 35 has
  no handoff success criterion, but a standalone checklist that `/gsd-complete-milestone` can read on
  its own is worth the file. Known items to include are in `<specifics>`.

- **D-10: Phase 35 creates the WR-01 todo file; the REL-03 checkbox flip stays on the close side.**
  Write the todo now so the decision not to pick WR-01 up is recorded rather than lost. Measured:
  `.planning/REQUIREMENTS.md` has REL-03 at `[ ]` with traceability "Pending" — since prep completion
  is not yet a publish, flip it at ship/complete-milestone as before.

- **D-11: Do not rework `release.yml`'s release-notes body in v0.6.5; file it as a todo.** Measured:
  the v0.6.4 release body is 308 lines, of which lines 1–296 are the commit dump produced by
  `release.yml`'s "Generate release notes" step
  (`git log $PREV_TAG..$TAG --pretty="- %s (%h)"`, including planning commits like `docs(33-04): …`).
  Lines 297–303 are Installation; lines 304–308 are GitHub's own output from
  `generate_release_notes: true` (a one-line "What's Changed" PR entry plus the Full Changelog link) —
  **the auto-generated part is already compact; the bloat is entirely the hand-rolled `git log` block.**
  Design direction to record in the todo: drop the `git log` block, extract just the `## [X.Y.Z]`
  section from `CHANGELOG.md` as the body, and keep Installation and `generate_release_notes: true`.
  Also record the measured fact that **`release.yml` never reads `CHANGELOG.md`** — the Phase 33
  CONTEXT statement that "the `[0.6.4]` entry is the single source for the GitHub Release body"
  contradicts reality, and only becomes true once this todo is resolved.

### Scope of live-run evidence

- **D-12: Add the two docs dogfooding builds to the three runs SC#3 names.** On top of full pytest,
  `black` / `ruff` / `mypy`, and the full-corpus `-b typstpdf` gate, run `tox -e docs-html` and
  `tox -e docs-pdf` (the same three-item set as Phase 28 D-05, plus docs). Since this milestone
  touched the translator, confirm that the project's own docs still build under `typstpdf`.

### Claude's Discretion

The following are for the planner/executor to decide:

- The exact wording of the `[0.6.5]` CHANGELOG entry, the lead paragraph's phrasing, and how
  requirement IDs are attached
- The exact assertion strings for WR-02/03/04 (candidates are in the review's Fix fields) and the
  reST for Construct G
- Plan decomposition within the phase (D-07 fixes only the ordering: tests → version bump/CHANGELOG →
  evidence)
- The format and heading structure of `35-HANDOFF.md`
- The `uv.lock` regeneration procedure (acceptance: `uv sync --extra dev --locked` green)
- The wording, frontmatter, and filenames of the two todo files (WR-01 / `release.yml`)
- Where live-run evidence is recorded — note `35-VERIFICATION.md` is a name reserved by the verifier,
  so a plan that accumulates evidence must either use a different name or plan a backup-and-remerge

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Files to be changed

- `pyproject.toml` §`[project]` `:7` — `version = "0.6.4"` (measured: the sole version literal)
- `uv.lock` `:1379` — `typsphinx`'s `version = "0.6.4"`; regenerate to follow the bump
- `README.md:317` — `**Status**: Stable (v0.6.4) - Production ready`
- `CHANGELOG.md` — insert `## [0.6.5]` under `## [Unreleased]`. `## [0.6.4]` (lead paragraph +
  Added/Changed/Removed/Fixed/Verified) and `## [0.6.1]` (a small release: lead + Fixed + Verified)
  are the direct models for form. Updating the tail link block
  (`[0.6.4]: …/releases/tag/v0.6.4` and below, plus `[Unreleased]: …/compare/v0.6.4...HEAD`) is also
  this phase's job
- `tests/fixtures/inline_math_after_text_render_gate/index.rst` — Constructs A–F (D-06 adds G)
- `tests/test_inline_math_after_text_render_gate.py` — 345 lines, two tests (mitex / native); D-06
  adds assertions to both, and WR-03 / WR-04 live in the same file

### Gates and invariants

- `tests/test_readme_version_sync.py` — asserts the README Status line matches `pyproject.toml`'s
  version (forgetting the README during a bump turns it red)
- `tests/test_preview_version_sync.py` — the four-surface `@preview` sync (`typsphinx/writer.py` /
  `typsphinx/template_engine.py` / `typsphinx/templates/base.typ` / `examples/**/*.typ`)
- `tests/test_corpus_gate.py` — the full-corpus `-b typstpdf` gate (`-m slow`)
- `.planning/REQUIREMENTS.md` — REL-03's text (including the two-repository tagging standing cost),
  § Out of Scope (the five todos / v2 requirements / 30.1 Warnings are already decided as excluded),
  and § Traceability
- `.planning/ROADMAP.md` §Phase 35 — SC#1–SC#4 and the prep/publish fence (measured via
  `git rev-parse`: merge-base `eb696bb`, 33 commits)

### Prior-phase decisions and carry-forwards (handoff material)

- `.planning/phases/34-inline-math-after-text-separator-fix/34-REVIEW.md` §Warnings —
  WR-01 (`translator.py:4079-4088`) / WR-02 (`:4046-4055`) / WR-03 / WR-04. Each section's **Fix**
  field spells out candidate assertion strings (the implementation material for D-05–D-07)
- `.planning/phases/34-inline-math-after-text-separator-fix/34-VERIFICATION.md` — 5/5 SCs verified;
  the model for how SC#3/SC#4 evidence is written (verbatim command plus transcribed output)
- `.planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` — the RED→GREEN
  recording format
- `.planning/milestones/v0.6.4-phases/33-v0-6-4-release-prep/33-CONTEXT.md` — the most recent
  precedent for this phase type (how the CHANGELOG structure was decided, where the Verified line was
  drawn, how handoff items were ordered)
- `.planning/milestones/v0.6.3-phases/28-v0-6-3-release-prep-regression-gate-close/28-CONTEXT.md` —
  D-04's minimal-file principle and D-05's three-item evidence set (the precedent for D-12)
- `.planning/STATE.md` §Accumulated Context / §Deferred Items — standing decisions and the deferred
  item list

### Release machinery (D-11 todo material; not changed in this phase)

- `.github/workflows/release.yml` §`create-release` / the "Generate release notes" step — where the
  `git log` block causing the bloat sits alongside `generate_release_notes: true`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **The `## [0.6.1]` CHANGELOG entry** — the closest model for a small release (lead paragraph +
  Fixed + Verified). `## [0.6.4]` is the model on the many-sections end.
- **`tests/test_readme_version_sync.py` / `test_preview_version_sync.py` / `test_corpus_gate.py`** —
  the actual adjudicators for SC#1 / SC#3 / SC#4. No new implementation needed; run them and capture
  evidence.
- **The Fix fields in 34-REVIEW.md** — each of WR-02/03/04 already carries a concrete candidate
  assertion string. Nothing needs designing from scratch.
- **Verbatim command plus transcribed output** (the Phase 29 D-15 form) — the recording format for
  SC#3 / SC#4 evidence.

### Established Patterns

- **Prep and publish stay separate** — the final phase goes as far as the version bump and CHANGELOG;
  the irreversible publish happens at `/gsd-complete-milestone`.
- **Keep the touched-file set minimal** (Phase 28 D-04's four-file principle). This phase is wider by
  two test files, the HANDOFF, and two todos — but `docs/` and `typsphinx/` stay untouched.
- **The GATE-01 bar** (since v0.6.0) — every node-handler change ships a real-compile regression
  fixture. This phase does not touch the translator, so no new GATE-01 is needed; only gaps in the
  existing fixture get filled.
- **The honest-verifier convention** — never assert a truth without direct evidence; state
  unmeetable criteria as unmet.

### Integration Points

- **`/gsd-complete-milestone`** — this phase's `[0.6.5]` entry and `35-HANDOFF.md` are its inputs.
  Tag / PyPI / GitHub Release / PR merge / the translations repository's second tag / the
  REQUIREMENTS bookkeeping all happen over there.
- **`release.yml`** — fires on a `v0.6.5` tag push. This phase neither edits nor triggers it.
  Measured: the workflow does not read `CHANGELOG.md`; the release body is built from `git log`.
- **RTD (owner-manual, post-tag)** — confirm `stable` rebuilds at `v0.6.5` for both the parent and
  translations projects. Both Default Versions were flipped to `stable` at the v0.6.4 close
  (measured from STATE.md), so no flip work is expected this time.

</code_context>

<specifics>
## Specific Ideas

### Facts measured during the discussion (plans may take these as given)

| Claim | Measured result | Impact |
|---|---|---|
| Where the version literal lives | `pyproject.toml:7` only | Bump targets: that one site plus `README.md:317` and `uv.lock:1379` |
| CHANGELOG tail | Lines exist down to `[0.6.4]`; `[Unreleased]: …/compare/v0.6.4...HEAD` | Add the `[0.6.5]` line and advance the compare |
| Milestone diff | merge-base `eb696bb`, 33 commits. Non-planning changes: `typsphinx/translator.py` +45 lines / `tests/test_inline_math_after_text_render_gate.py` 345 lines / 2 fixture files (473 insertions, 0 deletions) | SC#4's diff range. Zero deletions makes the invariant assertion straightforward |
| Shapes already green before the fix | Fixture Construct A (top-level paragraph, including `text\ :math:`x`\ text`) | The basis for D-01's wording |
| Shapes that were red | Construct B (bullet-list item) / C (confval field body) / D (definition-list term) / E (display math inside a list item) / F (a list item whose sole content is inline math) | D-01 / D-02 |
| Phase 34 review | critical 0 / warning 4, still `status: issues_found` | D-05 |
| Translations-repo tags | `typsphinx-doc-translations` has only `v0.6.4` | D-08 |
| RTD versions | en `stable` = tag `v0.6.4` (identifier `2bf6ef3`); `/en/stable/` and `/ja/stable/` both 200 | D-08 |
| This milestone's `docs/` diff | Empty (`git diff --name-only … -- docs/` returns nothing) | The basis for D-08's "content is identical" judgement |
| v0.6.4 release body | 308 lines. Lines 1–296 = `release.yml`'s `git log` dump; 297–303 = Installation; 304–308 = GitHub auto-generated (1 PR line + Full Changelog) | D-11 |
| REQUIREMENTS state | MATH-01 is `[x]` / traceability "Complete"; REL-03 is `[ ]` / "Pending" | D-10 |

### Known items for `35-HANDOFF.md` (format at Claude's discretion)

1. Open the PR → merge (`/gsd-complete-milestone`)
2. Push tag `v0.6.5` → `release.yml` → PyPI + GitHub Release
3. **Bump the submodule and tag `v0.6.5` in the translations repository `typsphinx-doc-translations`**
   (D-08 / the v0.6.4 D-07 standing cost — `/ja/stable/` resolves against that repo's own tags)
4. After the tag build, confirm `stable` is green at `v0.6.5` for both projects (RTD's public API
   needs no auth; the Default Version flips were already done at the v0.6.4 close)
5. Flip the REL-03 checkbox and traceability row in `.planning/REQUIREMENTS.md` (D-10)
6. Confirm the two todos this phase files (WR-01 / the `release.yml` release body) are sitting in
   `.planning/todos/pending/` — candidates for the v0.6.6 scope

</specifics>

<deferred>
## Deferred Ideas

- **WR-01: `visit_math_block`'s redundant blank line** (`typsphinx/translator.py:4079-4088`) — the
  pre-existing unconditional `"\n\n"` and the new `list_item_needs_separator` flag both separate, so
  block math is followed by one extra blank line. Inert in Typst, but it diverges from every other
  block-level handler and will keep showing up as unexplained noise in future emitted-`.typ` diffs.
  D-05 leaves it out of Phase 35 and files it as a todo. Two fix options are given in the review's Fix
  field (drop the new block, or gate the pre-existing `"\n\n"` on `not self.in_list_item`).

- **Reworking `release.yml`'s release-notes body** (D-11) — drop the `git log` block and extract the
  `## [X.Y.Z]` section from `CHANGELOG.md` as the body, keeping Installation and
  `generate_release_notes: true`. Deferred out of v0.6.5 and filed as a todo for v0.6.6+.

### Reviewed Todos (not folded)

`todo.match-phase 35` returned five items, but every one is **already excluded** by
`.planning/REQUIREMENTS.md` § Out of Scope, so folding was not re-litigated:

- `2026-07-22-add-sphinx-linkcheck-ci-job.md` (score 0.6) — parked as Future requirement LNK-01
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` (0.6) — requires source changes;
  excluded by invariant #3
- `2026-07-22-citation-node-support-untracked.md` (0.4) — same
- `2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` (0.4) — same
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md` (0.4) — same

- **The three 30.1-review Warnings** (`contributing.rst` missing a toolchain-install step /
  `docs/source/_typst/custom_template.typ` being an unguarded fourth `@preview` lockstep site / no
  structural test coverage over the translations-repo manifests) — excluded from v0.6.5 by
  REQUIREMENTS § Out of Scope.

</deferred>

---

*Phase: 35-v0.6.5 Release Prep*
*Context gathered: 2026-07-28*
